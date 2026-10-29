// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "TesseractOSiOS",
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [.library(name: "TesseractOSiOS", targets: ["TesseractOSiOS"])],
    targets: [
        .target(name: "TesseractOSiOS", path: "IOS_EXPORT", sources: ["TESSERACT_OS_iOS.swift"]),
        .testTarget(name: "TesseractOSiOSTests", dependencies: ["TesseractOSiOS"], path: "Tests/TesseractOSiOSTests")
    ]
)
