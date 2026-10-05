import Foundation
import AVFoundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else { print("usage: personmatte <in.mov> <outdir>"); exit(1) }
let inURL = URL(fileURLWithPath: args[1])
let outDir = args[2]
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

let asset = AVAsset(url: inURL)
let track = asset.tracks(withMediaType: .video).first!
let reader = try! AVAssetReader(asset: asset)
let output = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
reader.add(output)
reader.startReading()

let ctx = CIContext()
var i = 0
let w = Int(track.naturalSize.width), h = Int(track.naturalSize.height)
while let sb = output.copyNextSampleBuffer() {
    guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
    let req = VNGeneratePersonSegmentationRequest()
    req.qualityLevel = .accurate
    req.outputPixelFormat = kCVPixelFormatType_OneComponent8
    let handler = VNImageRequestHandler(cvPixelBuffer: pb, options: [:])
    try! handler.perform([req])
    guard let mask = req.results?.first?.pixelBuffer else { continue }
    var ci = CIImage(cvPixelBuffer: mask)
    let mw = CGFloat(CVPixelBufferGetWidth(mask)), mh = CGFloat(CVPixelBufferGetHeight(mask))
    ci = ci.transformed(by: CGAffineTransform(scaleX: CGFloat(w)/mw, y: CGFloat(h)/mh))
    let cg = ctx.createCGImage(ci, from: CGRect(x: 0, y: 0, width: w, height: h))!
    let rep = NSBitmapImageRep(cgImage: cg)
    let png = rep.representation(using: .png, properties: [:])!
    try! png.write(to: URL(fileURLWithPath: String(format: "%@/m_%05d.png", outDir, i)))
    i += 1
    if i % 30 == 0 { print("frame \(i)"); fflush(stdout) }
}
print("done \(i) frames \(w)x\(h)")
