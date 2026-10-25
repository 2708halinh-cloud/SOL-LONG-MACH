"""Capability and privacy gate. No silent external media or text transfers."""
from __future__ import annotations
import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib import request,parse,error

MAX_TEXT = 12000
MAX_MEDIA = 9_000_000

def analyze_text(text: str) -> dict:
    if not isinstance(text,str) or not text.strip() or len(text)>MAX_TEXT:
        raise ValueError("TEXT_EMPTY_OR_OVERSIZE")
    # A reproducible, limited heuristic, NOT a trained emotion classifier.
    positive={"vui","hạnh phúc","tốt","cảm ơn","hy vọng","great","happy","good","love"}
    negative={"buồn","đau","giận","lo lắng","sợ","mất","sad","angry","bad","fear"}
    low=text.casefold()
    pos=sorted(x for x in positive if x in low)
    neg=sorted(x for x in negative if x in low)
    entities=[]
    for m in re.finditer(r"\b[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,3}",text):
        token=m.group()
        if token not in entities:
            entities.append(token)
    label="positive" if len(pos)>len(neg) else "negative" if len(neg)>len(pos) else "mixed_or_neutral"
    return {"mode":"HEURISTIC_NOT_MODEL_INFERENCE","sentiment":label,
            "positive_cues":pos,"negative_cues":neg,"entity_candidates":entities[:24],
            "entities_verified":False,"emotion_subjectively_felt":None}

def configured() -> dict:
    g=bool(os.getenv("SOL_GOOGLE_CLOUD_API_KEY"))
    return {
        "text_entities_sentiment":{"state":"READY_LOCAL_HEURISTIC","provider":"local_keyword_baseline"},
        "personal_research":{"state":"READY_LOCAL_SOURCED_EVENTS","provider":"sqlite"},
        "translation_basic":{"state":"CONNECTABLE" if g else "REQUIRES_ENV_SOL_GOOGLE_CLOUD_API_KEY","provider":"Google Cloud Translation Basic v2"},
        "image_details":{"state":"CONNECTABLE" if g else "REQUIRES_ENV_SOL_GOOGLE_CLOUD_API_KEY","provider":"Cloud Vision API (faces,landmarks,logos,objects)"},
        "transcription_mp3_mp4":{"state":"CONNECTABLE" if shutil.which("whisper") and shutil.which("ffmpeg") else "REQUIRES_LOCAL_WHISPER_AND_FFMPEG","provider":"local_whisper_cli"},
        "video_objects_saved":{"state":"CONNECTABLE" if g and shutil.which("ffmpeg") else "REQUIRES_CLOUD_VISION_KEY_AND_FFMPEG","provider":"bounded_ffmpeg_frames_plus_vision"},
        "video_stream_frames":{"state":"CONNECTABLE" if g else "REQUIRES_ENV_SOL_GOOGLE_CLOUD_API_KEY","provider":"caller_supplied_frames_plus_vision"},
        "video_action_recognition":{"state":"NOT_IMPLEMENTED_NEEDS_ACTION_MODEL","provider":None},
    }

def _json_post(url: str, payload: dict, *, timeout=25) -> dict:
    raw=json.dumps(payload).encode("utf-8")
    req=request.Request(url,data=raw,headers={"Content-Type":"application/json"},method="POST")
    with request.urlopen(req,timeout=timeout) as response:
        data=response.read(1_500_000)
    return json.loads(data.decode("utf-8"))

def _key():
    key=os.getenv("SOL_GOOGLE_CLOUD_API_KEY")
    if not key:
        raise ValueError("GOOGLE_CLOUD_CREDENTIAL_NOT_CONFIGURED")
    return key

def _approved(approved):
    if approved is not True:
        raise ValueError("EXTERNAL_TRANSFER_REQUIRES_EXPLICIT_APPROVAL")

def translate(text:str,target:str,*,source="auto",approved=False):
    _approved(approved)
    if not isinstance(text,str) or not text.strip() or len(text)>5000:
        raise ValueError("TRANSLATION_TEXT_LIMIT")
    if not isinstance(target,str) or not re.fullmatch(r"[A-Za-z-]{2,12}",target):
        raise ValueError("TARGET_LANGUAGE_INVALID")
    if not re.fullmatch(r"[A-Za-z-]{2,12}",source):
        raise ValueError("SOURCE_LANGUAGE_INVALID")
    url="https://translation.googleapis.com/language/translate/v2?"+parse.urlencode({"key":_key()})
    request_body={"q":text,"target":target,"format":"text"}
    if source!="auto":
        request_body["source"]=source
    res=_json_post(url,request_body)
    value=res.get("data",{}).get("translations",[])
    if not value:
        raise ValueError("PROVIDER_NO_TRANSLATION")
    return {"translation":value[0].get("translatedText"),"source_language":value[0].get("detectedSourceLanguage",source),
            "provider":"GOOGLE_TRANSLATION_BASIC_RESPONSE","provider_called":True}

def _decoded(b64):
    if not isinstance(b64,str) or len(b64)>MAX_MEDIA*2:
        raise ValueError("MEDIA_OVERSIZE")
    try:
        binary=base64.b64decode(b64,validate=True)
    except Exception as exc:
        raise ValueError("MEDIA_BASE64_INVALID") from exc
    if not binary or len(binary)>MAX_MEDIA:
        raise ValueError("MEDIA_OVERSIZE")
    return binary

def image_details(image_b64,*,approved=False):
    _approved(approved)
    data=_decoded(image_b64)
    if not (data.startswith(b"\xff\xd8\xff") or data.startswith(b"\x89PNG\r\n\x1a\n")):
        raise ValueError("ONLY_JPEG_OR_PNG")
    url="https://vision.googleapis.com/v1/images:annotate?"+parse.urlencode({"key":_key()})
    features=[{"type":x,"maxResults":12} for x in ("FACE_DETECTION","LANDMARK_DETECTION","LOGO_DETECTION","OBJECT_LOCALIZATION")]
    body={"requests":[{"image":{"content":base64.b64encode(data).decode("ascii")},"features":features}]}
    obj=_json_post(url,body)
    item=(obj.get("responses") or [{}])[0]
    if item.get("error"):
        raise ValueError("VISION_PROVIDER_REPORTED_ERROR")
    return {"provider":"GOOGLE_VISION_RESPONSE","provider_called":True,
            "faces":[{"bounds":v.get("boundingPoly",{}),"expressions_reported_by_provider":v.get("joyLikelihood")}
                     for v in item.get("faceAnnotations",[])][:12],
            "landmarks":[{"name":v.get("description"),"score":v.get("score")} for v in item.get("landmarkAnnotations",[])][:12],
            "logos":[{"name":v.get("description"),"score":v.get("score")} for v in item.get("logoAnnotations",[])][:12],
            "objects":[{"name":v.get("name"),"score":v.get("score"),"bounds":v.get("boundingPoly")}
                       for v in item.get("localizedObjectAnnotations",[])][:12],
            "face_identity_recognized":False,"image_bytes_persisted":False}

def transcribe_local(media_b64:str,filename:str):
    if not (shutil.which("whisper") and shutil.which("ffmpeg")):
        raise ValueError("LOCAL_TRANSCRIBER_NOT_AVAILABLE")
    if not isinstance(filename,str) or not filename.lower().endswith((".mp3",".mp4",".wav",".m4a")):
        raise ValueError("UNSUPPORTED_MEDIA_EXTENSION")
    data=_decoded(media_b64)
    suffix=Path(filename).suffix.lower()
    with tempfile.TemporaryDirectory(prefix="sol-speech-") as directory:
        media=Path(directory)/("source"+suffix)
        media.write_bytes(data)
        cmd=["whisper",str(media),"--model","tiny","--output_format","txt",
             "--output_dir",directory,"--fp16","False"]
        result=subprocess.run(cmd,check=False,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,timeout=120)
        if result.returncode:
            raise ValueError("LOCAL_TRANSCRIBER_FAILED")
        transcript=(Path(directory)/"source.txt")
        if not transcript.exists():
            raise ValueError("TRANSCRIPT_NOT_CREATED")
        return {"text":transcript.read_text(encoding="utf-8")[:20000],
                "provider":"LOCAL_WHISPER_CLI","provider_called":False,
                "media_persisted_after_request":False}

def video_objects(video_b64:str,*,approved=False):
    _approved(approved)
    if not shutil.which("ffmpeg"):
        raise ValueError("FFMPEG_NOT_AVAILABLE")
    data=_decoded(video_b64)
    with tempfile.TemporaryDirectory(prefix="sol-vision-") as directory:
        source=Path(directory)/"clip.mp4"
        source.write_bytes(data)
        framepattern=str(Path(directory)/"frame_%02d.jpg")
        cmd=["ffmpeg","-nostdin","-loglevel","error","-y","-i",str(source),
             "-vf","fps=1/5,scale='min(640,iw)':-1","-frames:v","3",framepattern]
        proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=35)
        if proc.returncode:
            raise ValueError("VIDEO_FRAME_EXTRACTION_FAILED")
        frames=sorted(Path(directory).glob("frame_*.jpg"))[:3]
        if not frames:
            raise ValueError("NO_VIDEO_FRAMES")
        results=[{"frame":i,"objects":image_details(base64.b64encode(p.read_bytes()).decode(),approved=True)["objects"]}
                 for i,p in enumerate(frames)]
    return {"frames":results,"provider":"LOCAL_FFMPEG_PLUS_GOOGLE_VISION",
            "provider_called":True,"action_recognition":"NOT_AVAILABLE_WITH_OBJECT_DETECTION",
            "video_persisted_after_request":False}
