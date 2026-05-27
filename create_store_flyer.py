from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M
except ImportError:  # pragma: no cover - optional helper dependency
    qrcode = None
    ERROR_CORRECT_M = None


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "marketing"
STEAM_ASSET_DIR = OUT_DIR / "steam_assets"

WEBSITE_URL = "https://teymurianstudios.github.io/teymurian-studios/"
STEAM_URL = "https://store.steampowered.com/app/4706510/The_Pharhad_Road"
ITCH_URL = "https://teymurian-studios.itch.io/tpr"
INSTAGRAM_URL = "https://www.instagram.com/teymurian_studios"

FLYER_PNG = OUT_DIR / "the_pharhad_road_store_flyer.png"
FLYER_PDF = OUT_DIR / "the_pharhad_road_store_flyer.pdf"
QR_PNG = OUT_DIR / "teymurian_studios_qr.png"

STEAM_CAPSULE = STEAM_ASSET_DIR / "capsule_616x353.jpg"
STEAM_HEADER = STEAM_ASSET_DIR / "header.jpg"
STEAM_SCREENSHOT = STEAM_ASSET_DIR / "screenshot_1920x1080.jpg"

W, H = 2550, 3300  # 8.5 x 11 inches at 300 dpi
DPI = 300


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    fonts = Path("C:/Windows/Fonts")
    return ImageFont.truetype(str(fonts / name), size)


FONT_TITLE = font("bahnschrift.ttf", 176)
FONT_TITLE_SMALL = font("bahnschrift.ttf", 76)
FONT_HEADING = font("arialbd.ttf", 86)
FONT_SUBHEAD = font("arialbd.ttf", 54)
FONT_BODY = font("arial.ttf", 44)
FONT_BODY_BOLD = font("arialbd.ttf", 44)
FONT_SMALL = font("arial.ttf", 31)
FONT_TINY = font("arial.ttf", 24)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    spacing: int = 8,
) -> None:
    lines = wrap_text(draw, text, fnt, box[2] - box[0])
    total_h = sum(text_size(draw, line, fnt)[1] for line in lines) + spacing * (len(lines) - 1)
    y = box[1] + ((box[3] - box[1]) - total_h) // 2
    for line in lines:
        tw, th = text_size(draw, line, fnt)
        draw.text((box[0] + ((box[2] - box[0]) - tw) // 2, y), line, font=fnt, fill=fill)
        y += th + spacing


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = word if line == "" else f"{line} {word}"
        if text_size(draw, candidate, fnt)[0] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 12,
) -> int:
    y = xy[1]
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((xy[0], y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + line_gap
    return y


def cover_image(src: Image.Image, size: tuple[int, int], crop_center: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / src.width, target_h / src.height)
    resized = src.resize((round(src.width * scale), round(src.height * scale)), Image.Resampling.LANCZOS)
    cx = int(resized.width * crop_center[0])
    cy = int(resized.height * crop_center[1])
    left = max(0, min(resized.width - target_w, cx - target_w // 2))
    top = max(0, min(resized.height - target_h, cy - target_h // 2))
    return resized.crop((left, top, left + target_w, top + target_h))


def fit_image(src: Image.Image, max_size: tuple[int, int]) -> Image.Image:
    max_w, max_h = max_size
    scale = min(max_w / src.width, max_h / src.height)
    return src.resize((round(src.width * scale), round(src.height * scale)), Image.Resampling.LANCZOS)


def make_qr() -> Image.Image:
    if qrcode is None:
        if QR_PNG.exists():
            return Image.open(QR_PNG).convert("RGB")
        raise SystemExit("Install qrcode first or keep teymurian_studios_qr.png in marketing/.")
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=18, border=4)
    qr.add_data(WEBSITE_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#101820", back_color="white").convert("RGB")
    img.save(QR_PNG)
    return img


def make_flyer() -> tuple[Image.Image, list[tuple[int, int, int, int, str]]]:
    links: list[tuple[int, int, int, int, str]] = []
    img = Image.new("RGBA", (W, H), "#f6f1e6")
    draw = ImageDraw.Draw(img)

    gold = "#f4c542"
    dark = "#101820"
    panel = "#182436"
    ink = "#101820"
    muted = "#506070"
    green = "#2fbf71"
    red = "#d64a4a"
    blue = "#36a3ff"

    # Top brand bar
    draw.rectangle((0, 0, W, 135), fill=gold)
    draw.text((145, 39), "TEYMURIAN STUDIOS", font=FONT_TITLE_SMALL, fill=dark)
    draw.text((W - 1240, 50), "A Persian-inspired tactical RPG", font=FONT_BODY_BOLD, fill=dark)

    # Hero field using official Steam store graphics.
    hero_y0, hero_y1 = 135, 1510
    draw.rectangle((0, hero_y0, W, hero_y1), fill=dark)

    screenshot = Image.open(STEAM_SCREENSHOT).convert("RGBA")
    screenshot_bg = cover_image(screenshot, (W, hero_y1 - hero_y0), (0.66, 0.48))
    img.alpha_composite(screenshot_bg, (0, hero_y0))
    img.alpha_composite(Image.new("RGBA", screenshot_bg.size, (8, 14, 22, 172)), (0, hero_y0))

    capsule = Image.open(STEAM_CAPSULE).convert("RGB")
    capsule_large = fit_image(capsule, (1430, 820)).convert("RGBA")
    cap_x, cap_y = 120, 260
    shadow = Image.new("RGBA", (capsule_large.width + 46, capsule_large.height + 46), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((16, 16, shadow.width - 16, shadow.height - 16), radius=34, fill=(0, 0, 0, 125))
    img.alpha_composite(shadow, (cap_x - 23, cap_y - 9))
    draw.rounded_rectangle(
        (cap_x - 12, cap_y - 12, cap_x + capsule_large.width + 12, cap_y + capsule_large.height + 12),
        radius=22,
        fill="#f4c542",
    )
    img.alpha_composite(capsule_large, (cap_x, cap_y))

    header = Image.open(STEAM_HEADER).convert("RGB")
    header_img = fit_image(header, (610, 230)).convert("RGBA")
    hx, hy = 1790, 275
    draw.rounded_rectangle((hx - 16, hy - 16, hx + header_img.width + 16, hy + header_img.height + 16), radius=18, fill="#0b1119", outline=gold, width=5)
    img.alpha_composite(header_img, (hx, hy))

    draw.text((1660, 575), "Enemies wake", font=FONT_HEADING, fill=gold)
    draw.text((1660, 665), "when they see you.", font=FONT_HEADING, fill="#ffffff")
    draw_wrapped(
        draw,
        (1660, 800),
        "A compact Persian-inspired tactical RPG where one careful move can control the fight, and one bad step can wake the road.",
        FONT_BODY,
        "#f7f3df",
        720,
        16,
    )

    # Small mode badges
    badges = [
        ("Lead Pahlavans", blue),
        ("Command Divs", red),
        ("Send Dastur Z", green),
        ("Pahlavan Chess", gold),
    ]
    x = 145
    y = 1350
    for label, color in badges:
        tw, th = text_size(draw, label, FONT_SMALL)
        rect = (x, y, x + tw + 44, y + 72)
        draw.rounded_rectangle(rect, radius=18, fill="#0b1119", outline=color, width=5)
        draw.text((x + 22, y + 18), label, font=FONT_SMALL, fill="#ffffff")
        x = rect[2] + 24

    # Main body
    draw.rectangle((0, hero_y1, W, H), fill="#f6f1e6")
    draw.text((145, 1630), "Survive four dangerous roads.", font=FONT_HEADING, fill=ink)
    draw_wrapped(
        draw,
        (145, 1740),
        "Scout sight lines. Protect the wounded. Spend scarce recovery tools. Then decide whether to press forward before the next fight wakes up.",
        FONT_BODY,
        muted,
        1270,
        18,
    )

    features = [
        ("Grid tactics", "Move, aim, heal, shove, and survive on a readable tactical map."),
        ("Line of sight", "Enemies join the fight when they spot you."),
        ("Dice drama", "Critical hits, saves, misses, prone turns, and clutch recoveries."),
        ("More modes", "Lead pahlavans, command divs, call Pharhad, send Dastur Z, or practice in Pahlavan Chess."),
    ]
    fy = 2005
    for heading, body in features:
        draw.rounded_rectangle((145, fy, 1345, fy + 175), radius=24, fill="#ffffff", outline="#d9d0bd", width=4)
        draw.ellipse((180, fy + 47, 250, fy + 117), fill=gold, outline=ink, width=3)
        draw.text((285, fy + 34), heading, font=FONT_BODY_BOLD, fill=ink)
        draw_wrapped(draw, (285, fy + 92), body, FONT_SMALL, muted, 975, 7)
        fy += 205

    # QR and links panel
    qr = make_qr().resize((610, 610), Image.Resampling.NEAREST)
    qx, qy = 1715, 1640
    draw.rounded_rectangle((1595, 1585, 2405, 2925), radius=44, fill=panel, outline=gold, width=7)
    draw.text((1694, 1665), "SCAN TO PLAY", font=FONT_SUBHEAD, fill=gold)
    draw.rounded_rectangle((qx - 28, qy + 110 - 28, qx + 610 + 28, qy + 110 + 610 + 28), radius=28, fill="#ffffff")
    img.paste(qr, (qx, qy + 110))
    links.append((qx - 28, qy + 110 - 28, qx + 610 + 28, qy + 110 + 610 + 28, WEBSITE_URL))

    draw_wrapped(
        draw,
        (1660, 2400),
        "Scan for the website, Combat Codex, Steam page, and itch.io build.",
        FONT_BODY_BOLD,
        "#ffffff",
        690,
        12,
    )
    draw.text((1660, 2575), "teymurianstudios.github.io", font=FONT_SMALL, fill="#d5deea")
    links.append((1660, 2570, 2365, 2615, WEBSITE_URL))

    button_y = 2820
    for label, url, color in [
        ("Steam", STEAM_URL, "#22395f"),
        ("itch.io", ITCH_URL, "#7b2f37"),
        ("Website", WEBSITE_URL, "#28573e"),
        ("Instagram", INSTAGRAM_URL, "#7a346c"),
    ]:
        bw = 235 if label in ["Steam", "itch.io"] else 285 if label == "Website" else 340
        bx = 145 if label == "Steam" else 405 if label == "itch.io" else 665 if label == "Website" else 980
        draw.rounded_rectangle((bx, button_y, bx + bw, button_y + 86), radius=22, fill=color)
        draw_centered(draw, (bx, button_y, bx + bw, button_y + 86), label, FONT_BODY_BOLD, "#ffffff")
        links.append((bx, button_y, bx + bw, button_y + 86, url))

    draw.text((145, 2948), "Steam:", font=FONT_SMALL, fill=ink)
    draw.text((290, 2948), STEAM_URL.replace("https://", ""), font=FONT_SMALL, fill=muted)
    links.append((290, 2948, 1420, 2990, STEAM_URL))
    draw.text((145, 3010), "itch.io:", font=FONT_SMALL, fill=ink)
    draw.text((290, 3010), ITCH_URL.replace("https://", ""), font=FONT_SMALL, fill=muted)
    links.append((290, 3010, 1020, 3052, ITCH_URL))
    draw.text((145, 3072), "Website:", font=FONT_SMALL, fill=ink)
    draw.text((350, 3072), WEBSITE_URL.replace("https://", ""), font=FONT_SMALL, fill=muted)
    links.append((350, 3072, 1525, 3114, WEBSITE_URL))
    draw.text((145, 3134), "Instagram:", font=FONT_SMALL, fill=ink)
    draw.text((430, 3134), "@teymurian_studios", font=FONT_SMALL, fill=muted)
    links.append((430, 3134, 960, 3176, INSTAGRAM_URL))

    draw.line((145, 3195, W - 145, 3195), fill="#d9d0bd", width=4)
    draw.text(
        (145, 3228),
        "The Pharhad Road (c) Teymurian Studios. Artwork by DENZI, adapted, CC BY-SA 3.0.",
        font=FONT_TINY,
        fill="#6c6c6c",
    )

    return img.convert("RGB"), links


def save_pdf(png: Image.Image, links: list[tuple[int, int, int, int, str]]) -> None:
    c = canvas.Canvas(str(FLYER_PDF), pagesize=letter)
    page_w, page_h = letter
    c.drawImage(ImageReader(png), 0, 0, width=page_w, height=page_h)

    sx = page_w / W
    sy = page_h / H
    for x0, y0, x1, y1, url in links:
        c.linkURL(url, (x0 * sx, page_h - y1 * sy, x1 * sx, page_h - y0 * sy), relative=0)
    c.showPage()
    c.save()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    flyer, links = make_flyer()
    flyer.save(FLYER_PNG, dpi=(DPI, DPI), quality=95)
    save_pdf(flyer, links)
    print(FLYER_PNG)
    print(FLYER_PDF)
    print(QR_PNG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
