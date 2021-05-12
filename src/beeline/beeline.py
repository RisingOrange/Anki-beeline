import re

try:
    from ._vendor.bs4 import BeautifulSoup
except:
    from bs4 import BeautifulSoup


def lerp(v0, v1, t):
    # Linear interpolate between v0 and v1 at percent t
    return v0 * (1 - t) + v1 * t


def hex_to_rgb(h):
    # Convert a hex triplet (#XXXXXX) to an array containing red, green, and blue
    h = h[1:]
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def lines(html):
    return re.split('<br>|<br/>|<br/ >', html)


def beeline(html):
    COLORS = ["#0000FF", "#FF0000"]
    COLOR_TEXT = "#000000"
    BASE_COLOR = hex_to_rgb(COLOR_TEXT)
    GRADIENT_SIZE = 50

    result = ''
    coloridx = 0
    for lineno, line in enumerate(lines(html)):
        if not line:
            continue

        # Alternate between left and right for every color
        active_color = hex_to_rgb(COLORS[coloridx])

        # Color lines using lerp of RGB values
        rgb_strings = []
        for idx, _ in enumerate(remove_html_tags(line)):
            t = 1 - (idx / (len(line) * GRADIENT_SIZE / 50))
            red = lerp(BASE_COLOR[0], active_color[0], t)
            green = lerp(BASE_COLOR[1], active_color[1], t)
            blue = lerp(BASE_COLOR[2], active_color[2], t)

            rgb_strings.append(f'rgb({int(red)},{int(green)},{int(blue)})')

        # Flip array around if on left to color correctly
        is_left = lineno % 2 == 0
        if is_left:
            rgb_strings = list(reversed(rgb_strings))

        # Increment color index after every left/right pair
        if not is_left:
            coloridx = (coloridx + 1) % len(COLORS)

        line = wrap_chars(line, rgb_strings)
        result += str(line) + '<br>'

    return result[:len(result) - len('<br>')]


def unbeeline(html):
    soup = BeautifulSoup(html, 'html.parser')
    for x in soup.find_all('span', {'class': 'beeline'}):
        x.replace_with(x.text)
    return str(soup)


def remove_html_tags(html):
    soup = BeautifulSoup(html, features='html.parser')
    return soup.text


def wrap_chars(html, rgb_strings):
    rgb_strings_iter = iter(rgb_strings)
    soup = BeautifulSoup(html, features='html.parser')
    for x in list(soup.strings):
        topspan = soup.new_tag('span')
        topspan['class'] = 'beeline'
        for char in str(x):
            span = soup.new_tag('span')
            span.string = str(char)
            span['style'] = f"color: {next(rgb_strings_iter)}"
            topspan.append(span)
        x.replace_with(topspan)

    return str(soup)


if __name__ == '__main__':
    with open('input.html') as f:
        result = beeline(f.read())

    with open('result.html', 'w') as f:
        f.write(result)
