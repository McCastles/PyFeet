# PyFeet
Final project for the Python class in Warsaw University of Technology.

### The problem 

This application serves the goal of visualization the data, gathered from six pressure sensors, placed on a special shoes. The experiment is meant to reveal anomalies when compared to a healthy foot.

### Data gathering

The main source of the data is [the server](http://tesla.iem.pw.edu.pl:9080/v2/monitor/2) of the Elektryczny Faculty on WUT. In order to access it, one needs to establish a [VPN connection](https://vpn.ee.pw.edu.pl). The full API can be found [here](http://tesla.iem.pw.edu.pl:9080/v2/static/index.html).

### Usage

Navigate to ```walk_monitoring/source/``` and type ```python main_app.py``` in the console, then open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in your browser (better looks on Firefox).

Alternative start may be performed by executing ```api_mockup.py``` to imitate the activity of the real Tesla server, thus VPN is not needed.

### Details

Full project description can be found [here](https://github.com/McCastles/PyFeet/blob/master/docs/PyFeet.pdf).
