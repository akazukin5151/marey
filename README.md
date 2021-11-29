# train schedule diagram

A python script that scrapes [ekitan](ekitan.com/) (a Japanese transportation routing service) to make a train schedule diagram

![chuo_normal](examples/plots/chuo_normal.png)

![chuo_delta](examples/plots/chuo_delta.png)

![chuo_delta_scatter](examples/plots/chuo_delta_scatter.png)

![chuo_sobu_normal](examples/plots/chuo_sobu_normal.png)

![chuo_sobu_delta](examples/plot/chuo_sobu_delta.png)

![chuo_sobu_delta_scatter](examples/plot/chuo_sobu_delta_scatter.png)

![keihin_tohoku_normal](examples/plots/keihin_tohoku_normal.png)

![keihin_tohoku_delta](examples/plotters/keihin_tohoku_delta.png)

![keihin_tohoku_delta_scatter](examples/plotters/keihin_tohoku_delta_scatter.png)

![takasaki_normal](examples/plotters/takasaki_normal.png)

![takasaki_delta](examples/plotters/takasaki_delta.png)

![takasaki_delta_scatter](examples/plotters/takasaki_delta_scatter.png)

![yamanote_normal](examples/plotters/yamanote_normal.png)

![yamanote_delta](examples/plotters/yamanote_delta.png)

![yamanote_delta_scatter](examples/plotters/yamanote_delta_scatter.png)

# Features

- Can start from any station, not just line terminus
- Multiple plotters available
    - Non-interactive matplotlib
    - Interactive bokeh
    - Interactive Altair/Vega (Note: rather slow for large data sets)

# Install dependencies

Install the dependencies with `pip install -r requirements.txt`

Bokeh and Altair is optional, it is only used for interactive plots and depends on your choice

# Running

Either edit the bottom of main.py to use your own url and line name, and line color

Or from another python module, import `main` and call `main.main(line)`, giving your own `line`. To construct a `Line`, import `common` and call `common.Constants.Line`

Note that your url should be pinned to a specific date, not current results. See:

- NO: 'https://ekitan.com/timetable/railway/line-station/180-0/d1'
- YES: 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'

All the scripts will try its best to immediately return if their output file already exists (regardless if the file is correct). To force the scripts to run, delete their output files

# Q&A

- Why not use the JR website? [Eg](https://www.jreast-timetable.jp/2112/timetable/tt1039/1039090.html)

Because it does not have arrival and departure time, only an instantaneous time

# See also
- https://mbtaviz.github.io/
- https://blog.data.gov.sg/how-we-caught-the-circle-line-rogue-train-with-data-79405c86ab6a
- https://yewtu.be/watch?v=NFLb1IPlY_k
