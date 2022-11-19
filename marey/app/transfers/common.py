from dataclasses import dataclass

CssClass = str

@dataclass
class Route:
    date: str
    time: str
    start: str
    end: str
    filename: str
    result_idx: int

    def to_url(self):
        return f'https://ekitan.com/transit/route/sf-1627/st-2962?sfname={self.start}&stname={self.end}&dt={self.date}&tm={self.time}'
