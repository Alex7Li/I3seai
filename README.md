# I3seai
Watch the Accompanying YouTube Video: [here](https://www.youtube.com/watch?v=_GN8-LTqp2g)

Using Aporia for a movie reccomendation system.
https://www.aporia.com

To run:

Run the following files after connecting to a kafka stream
```
ssh -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf
```
1. aporia_ratinglogger.py
2. use_aporia.py