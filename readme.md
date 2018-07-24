# WE1S Chomp

WE1S Chomp is a client-side, human-assisted, generic-ish web scraper designed to collect broad data samples from specific websites based on specific Google queries. It should (eventually) be extensible, user-friendly, and capable of producing good, clean results at the scale of thousands or tens of thousands of queries.


## Installing

**Option One:** Clone the repo and install manually with ```pip```.

``` 
git clone https://github.com/seangilleran/we1schomp.git
pip install -r requirements.txt
```

 WE1S Chomp requires Python version 3.7 or later, available [here](https://www.python.org/downloads/release/python-370/), and the Selenium Chrome Driver, which is available [here](https://chromedriver.storage.googleapis.com/index.html?path=2.40/).

**Option Two:** Windows users can download the latest release, including a working Python virutal environment, [here](https://github.com/seangilleran/we1schomp/releases). Unzip the folder, edit ```settings.ini```, and run using the ```.bat``` files.


## Set-Up

WE1S Chomp works in two stages. First it collects lists of relevant URLs from Google, then it goes back and collects article content from those URLs. You can control all these operations from the ```settings.ini``` file.

Each website should have a section in ```settings.ini``` that includes information about it and any special instructions for it WE1S Chomp might require. **Do not include ```http://```, ```www.```, etc.** For example:

```ini
[thebaffler.com]
name = The Baffler
url_stops = .forum,/author,/contributor,/es/
output_path = output\\left

[theoutline.com]
name = The Outline
urls_only = True
```

Every website you query *must* have a section, and every section *must* have a proper name. All the other settings are optional. Any settings you do not specify will revert to the defaults provided under the heading ```[DEFAULT]```.


## URL Collection

Once you have configured ```settings.ini```, you can begin collecting URLs. Run this process by double-clicking ```get_urls.bat``` (Windows only) or with:

```
python we1schomp.py --urls_only
```

Eventually, Google will become suspicious and give you a CAPTCHA to complete to prove that you're not a bot. Fill this out in Chrome, return to the WE1S Chomp terminal, and press ```Enter```.


## Article Collection

Once you have a set of URL files in place, you can begin collecting articles. Run this process by double-clicking ```get_articles.bat``` (Windows only) or with:

```
python we1schomp.py --articles_only
```

WE1S Chomp works by grabbing all the content from the ```content_tag``` tags in ```settings.ini``` and throwing out anything with fewer than ```content_length_min``` characters. If you are not getting good results, you can change these on a per-site basis in ```settings.ini```.

### A Special Note for Those with Old URL Files

WE1S Chomp can read older URL files, but you need to do a few things to make them work.

First, place the files in ```output/urls```. Modify the filenames to add "```the```", "```-com```", "```-net```", etc. For instance, "```baffler_humanities_urls.json```" should be changed to "```thebaffler-com_humanities_urls.json```".

Second, make sure that each site has an entry in ```settings.ini```.

Finally, run article collection as normal.
