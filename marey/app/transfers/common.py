from dataclasses import dataclass

CssClass = str

@dataclass
class Route:
    url: str
    filename: str
    result_idx: int

    def date(self):
        dt_pos = self.url.find('dt')
        DATE_LEN = 8
        start = dt_pos + 3
        end = start + DATE_LEN
        return self.url[start:end]

