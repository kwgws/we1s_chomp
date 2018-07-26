# WE1S Chomp

WE1S Chomp is a client-side, human-assisted, generic-ish web scraper designed to collect broad data samples from specific websites based on specific Google queries. It should (eventually) be extensible, user-friendly, and capable of producing good, clean results at the scale of thousands or tens of thousands of queries.


## Installing

Clone the repo and install manually with ```pip```.

```bash
git clone https://github.com/seangilleran/we1schomp.git
cd we1schomp
pip install -r requirements.txt
```

 **IMPORTANT:** WE1S Chomp requires **Python 3.6 or later**, available [here](https://www.python.org/), and the **Selenium Chrome Driver**, (included).


## Set-Up

WE1S Chomp works in two stages. First it collects lists of relevant URLs from Google, then it goes back and collects article content from those URLs. You can control all these operations from the ```settings.ini``` file.

Each website should have a section in ```settings.ini``` that includes information about it and any special instructions for it WE1S Chomp might require. Many of the settings under ```[DEFAULT]``` can be changed for individual websites. For example:

```ini
...

[thebaffler]
name = The Baffler
url = thebaffler.com

[theoutline]
name = The Outline
url = theoutline.com
skip = true
```

Every website you query *must* have a section, and every section *must* have a URL and proper name. Do not include ```http://```, ```www.```, etc.All the other settings are optional. Any settings you do not specify will revert to the defaults provided under the heading ```[DEFAULT]```.


## URL Collection

Once you have configured ```settings.ini```, you can begin collecting URLs.

```bash
python run.py --urls_only
```

Eventually, Google will become suspicious and give you a CAPTCHA to complete to prove that you're not a bot. Fill this out in Chrome, return to the WE1S Chomp terminal, and press ```Enter```.


## Article Collection

Once you have a set of URL files in place, you can begin collecting articles.

```bash
python run.py --articles_only
```

WE1S Chomp works by grabbing all the content from the ```content_tag``` tags in ```settings.ini``` and throwing out anything with fewer than ```content_length_min``` characters. If you are not getting good results, you can change these on a per-site basis in ```settings.ini```.