import AVFoundation
import Vision
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let asset = AVAsset(url: url)
let track = asset.tracks(withMediaType: .video)[0]
let reader = try! AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
reader.add(out); reader.startReading()
while let sb = out.copyNextSampleBuffer() {
  let t = CMSampleBufferGetPresentationTimeStamp(sb).seconds
  guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
  let req = VNDetectFaceLandmarksRequest()
  try? VNImageRequestHandler(cvPixelBuffer: pb, options: [:]).perform([req])
  var v = -1.0
  if let f = req.results?.first, let lm = f.landmarks, let il = lm.innerLips, let fc = lm.faceContour {
    let p = il.normalizedPoints.map { Double($0.y) }
    let open = (p.max()! - p.min()!)
    let fy = fc.normalizedPoints.map { Double($0.y) }
    v = open / max(1e-6, (fy.max()! - fy.min()!))
  }
  print(String(format: "%.4f %.5f", t, v))
}
