import AVFoundation
import Vision
// t cx cy h  (normalizados, y desde arriba); -1 si no hay cara
let asset = AVAsset(url: URL(fileURLWithPath: CommandLine.arguments[1]))
let track = asset.tracks(withMediaType: .video)[0]
let reader = try! AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
reader.add(out); reader.startReading()
while let sb = out.copyNextSampleBuffer() {
  let t = CMSampleBufferGetPresentationTimeStamp(sb).seconds
  guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
  let req = VNDetectFaceRectanglesRequest()
  try? VNImageRequestHandler(cvPixelBuffer: pb, options: [:]).perform([req])
  if let f = req.results?.max(by: { $0.boundingBox.height < $1.boundingBox.height }) {
    let b = f.boundingBox
    print(String(format: "%.4f %.5f %.5f %.5f", t, b.midX, 1 - b.midY, b.height))
  } else { print(String(format: "%.4f -1 -1 -1", t)) }
}
