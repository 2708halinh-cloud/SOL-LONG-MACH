import unittest
import sol_video_engine as sv

class TestVideoEngine(unittest.TestCase):
    def test_prompt_without_mutating(self):
        source={'5': {'inputs': {'text': 'old'}, 'class_type': 'CLIPTextEncode'}, '8': {'inputs': {'image': 'old.png'}, 'class_type': 'LoadImage'}}
        updated=sv.mutate_workflow(source, 'mèo bay', '5', '8', 'cat.png')
        self.assertEqual(updated['5']['inputs']['text'], 'mèo bay')
        self.assertEqual(updated['8']['inputs']['image'], 'cat.png')
        self.assertEqual(source['5']['inputs']['text'], 'old')
    def test_prompt_alt_property(self):
        self.assertEqual(sv.mutate_workflow({'1': {'inputs': {'prompt': 'old'}}}, 'new', '1')['1']['inputs']['prompt'], 'new')
    def test_invalid_node(self):
        with self.assertRaisesRegex(ValueError, 'not found'):
            sv.mutate_workflow({'1': {'inputs': {'text': 'x'}}}, 'new', '2')
    def test_video_output(self):
        r={'outputs': {'12': {'videos': [{'filename': 'render.mp4','subfolder':'v','type':'output'}]}, '13': {'images': [{'filename':'thumb.png'}]}}}
        self.assertEqual([x['filename'] for x in sv.find_video_outputs(r)], ['render.mp4'])
    def test_bad_url(self):
        with self.assertRaises(ValueError):
            sv.ComfyClient('ftp://remote.invalid')

if __name__ == '__main__': unittest.main()
