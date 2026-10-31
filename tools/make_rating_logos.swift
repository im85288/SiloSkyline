// The rating sources' marks for the info page's facts line, drawn at 4x:
//   xcrun swift tools/make_rating_logos.swift fonts/Inter-Bold.ttf media/silo
// TMDB as Silo's Apple TV app shows it (green-to-teal letters, then a teal-to-blue
// pill); IMDb in its own colours (black letters on its yellow).
import Foundation
import CoreGraphics
import CoreText
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
let scale: CGFloat = 4
let space = CGColorSpaceCreateDeviceRGB()
let descriptors = CTFontManagerCreateFontDescriptorsFromURL(URL(fileURLWithPath: args[1]) as CFURL) as! [CTFontDescriptor]

func rgb(_ hex: Int) -> CGColor {
    CGColor(red: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255,
            blue: CGFloat(hex & 255) / 255, alpha: 1)
}

func context(_ width: CGFloat, _ height: CGFloat) -> CGContext {
    CGContext(data: nil, width: Int(width), height: Int(height), bitsPerComponent: 8, bytesPerRow: 0,
              space: space, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
}

func line(_ text: String, size: CGFloat, kern: CGFloat) -> CTLine {
    let font = CTFontCreateWithFontDescriptor(descriptors[0], size * scale, nil)
    return CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: [
        kCTFontAttributeName as NSAttributedString.Key: font,
        kCTKernAttributeName as NSAttributedString.Key: kern * scale]))
}

func save(_ ctx: CGContext, _ name: String) {
    let path = (args[2] as NSString).appendingPathComponent(name)
    let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(dest, ctx.makeImage()!, nil)
    CGImageDestinationFinalize(dest)
    print("wrote", path, ctx.width / Int(scale), "x", ctx.height / Int(scale))
}

// TMDB: the letters fill the height; a gap, then a pill 0.6 of their width.
do {
    let height: CGFloat = 30 * scale
    let letters = line("TMDB", size: 30, kern: 3.5)
    let bounds = CTLineGetImageBounds(letters, context(height, height))
    let width = (bounds.width * 1.62 + 7 * scale).rounded()
    let ctx = context(width, height)
    let top = (height - bounds.height) / 2
    ctx.saveGState()
    ctx.textPosition = CGPoint(x: -bounds.minX, y: top - bounds.minY)
    ctx.setTextDrawingMode(.clip)
    CTLineDraw(letters, ctx)
    let fill = CGGradient(colorsSpace: space, colors: [rgb(0x90CEA1), rgb(0x3CBEC9)] as CFArray, locations: [0, 1])!
    ctx.drawLinearGradient(fill, start: .zero, end: CGPoint(x: bounds.width, y: 0), options: [])
    ctx.restoreGState()
    let x = bounds.width + 7 * scale
    let pill = CGRect(x: x, y: top, width: width - x, height: bounds.height)
    ctx.addPath(CGPath(roundedRect: pill, cornerWidth: pill.height / 2, cornerHeight: pill.height / 2, transform: nil))
    ctx.clip()
    let blue = CGGradient(colorsSpace: space, colors: [rgb(0x3CBEC9), rgb(0x01B4E4)] as CFArray, locations: [0, 1])!
    ctx.drawLinearGradient(blue, start: CGPoint(x: pill.minX, y: 0), end: CGPoint(x: pill.maxX, y: 0), options: [])
    save(ctx, "tmdb.png")
}

// IMDb: black letters on its yellow, in a rounded box.
do {
    let height: CGFloat = 28 * scale
    let letters = line("IMDb", size: 19, kern: 0)
    let bounds = CTLineGetImageBounds(letters, context(height, height))
    let width = (bounds.width + 14 * scale).rounded()
    let ctx = context(width, height)
    ctx.addPath(CGPath(roundedRect: CGRect(x: 0, y: 0, width: width, height: height),
                       cornerWidth: 5 * scale, cornerHeight: 5 * scale, transform: nil))
    ctx.setFillColor(rgb(0xF5C518))
    ctx.fillPath()
    ctx.textPosition = CGPoint(x: (width - bounds.width) / 2 - bounds.minX, y: (height - bounds.height) / 2 - bounds.minY)
    ctx.setFillColor(rgb(0x000000))
    CTLineDraw(letters, ctx)
    save(ctx, "imdb.png")
}
