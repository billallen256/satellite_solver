A script that uses `pyorbital` to help find what satellite you saw passing overhead.

Pass in a file containing the TLE's to search, your latitude, your longitude, and the UTC time that you saw the satellite.

```sh
pipenv install  # just the first time
pipenv shell
python satellite_solver.py tle_file.txt 39.833333 -98.583333 20200831113951
```

Two Line Element (TLE) files available from Celestrak: http://www.celestrak.com/NORAD/elements/active.txt
