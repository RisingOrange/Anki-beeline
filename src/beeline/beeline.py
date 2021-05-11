import re

from ._vendor import bs4


def lerp(v0, v1, t):
    # Linear interpolate between v0 and v1 at percent t
    return v0 * (1 - t) + v1 * t


def hex_to_rgb(h):
    # Convert a hex triplet (#XXXXXX) to an array containing red, green, and blue
    h = h[1:]
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def lines(html):
    return html.split('<br>')


def beeline(html):
    result = ''

    COLORS = ["#0000FF", "#FF0000"]
    COLOR_TEXT = "#000000"
    BASE_COLOR = hex_to_rgb(COLOR_TEXT)
    GRADIENT_SIZE = 50

    coloridx = 0

    for lineno, line in enumerate(lines(html)):
        result_line = ''

        # Alternate between left and right for every color
        active_color = hex_to_rgb(COLORS[coloridx])

        # Color lines using lerp of RGB values
        rgb_strings = []
        for idx, _ in enumerate(line):
            t = 1 - (idx / (len(line) * GRADIENT_SIZE / 50))
            red = lerp(BASE_COLOR[0], active_color[0], t)
            green = lerp(BASE_COLOR[1], active_color[1], t)
            blue = lerp(BASE_COLOR[2], active_color[2], t)

            rgb_strings.append(f'rgb({int(red)},{int(green)},{int(blue)})')

        # Flip array around if on left to color correctly
        is_left = (lineno % 2 == 0)
        if is_left:
            rgb_strings = list(reversed(rgb_strings))

        for char, rgb_string in zip(line, rgb_strings):
            result_line += f'<span class="beeline" style="color: {rgb_string};">{char}</span>'

        # Increment color index after every left/right pair, and lineno
        # after every line
        if not is_left:
            coloridx = (coloridx + 1) % len(COLORS)

        result += result_line + '<br>'

    return result[:len(result) - len('<br>')]


def unbeeline(html):
    return re.sub(r'<span class="beeline".+?>(.)</span>', r'\1', html)


if __name__ == '__main__':
    with open('foo.txt') as f:
        result = beeline(f.read())

    print(unbeeline(result))

    with open('result.html', 'w') as f:
        f.write(result)
