```
██╗    ██╗███████╗ ██╗███████╗     ██████╗██╗  ██╗ ██████╗ ███╗   ███╗██████╗ 
██║    ██║██╔════╝███║██╔════╝    ██╔════╝██║  ██║██╔═══██╗████╗ ████║██╔══██╗
██║ █╗ ██║█████╗  ╚██║███████╗    ██║     ███████║██║   ██║██╔████╔██║██████╔╝
██║███╗██║██╔══╝   ██║╚════██║    ██║     ██╔══██║██║   ██║██║╚██╔╝██║██╔═══╝ 
╚███╔███╔╝███████╗ ██║███████║    ╚██████╗██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     
 ╚══╝╚══╝ ╚══════╝ ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     
```

**A Digital Humanities Web Scraper by Sean Gilleran and the WE1S Team**

## Installation

Set up a virtual machine, Docker container or other environment with Python >3.6
and the latest version of Jupyter Notebook.

Clone the repository to a working directory with:
`git clone https://github.com/seangilleran/we1s_chomp`

Move to the working directory and install the required Python packages:
`pip install -r requirements.txt`

Finally, install the we1s_chomp package:
`python -m setup.py build`
`python -m setup.py install`

At this point you should be all set to go. Start the import notebook if you
want to configure Chomp using CSV files, or write the JSON files by hand.

Chomp can also be used programmatically as a Python library. See documentation
in `google.py` and `wordpress.py` for more information.


### Environment Variables

The following environment variables must be enabled to properly run the
included Jupyter notebooks:

- `CHOMP_SELENIUM_GRID_URL`: URL of Selenium grid with at least one open
  Chrome node.
- `CHOMP_GOOGLE_CX`: ID string for a Google Custom Search Engine API.
- `CHOMP_GOOGLE_KEY`: Key string for a Google Custom Search Engine API.

For more information on the Google CSE API, consult the documentation at
https://developers.google.com/custom-search/v1/overview.


## Configuring Chomp Notebooks

The Chomp notebooks pull from a set of JSON manifest files (loosely)
governed by the [WE1S Schema](https://github.com/whatevery1says/manifest/).
You can place these wherever it is convenient for you. The default paths are
`./data/json/sources`, `./data/json/queries`, etc.

To scrape a website, you will need two things: a **Source** and a **Query**.

A **Source** is roughly equivalent to a domain name, although it also contains
important publisher metadata. As a **Source**, the WE1S Project's web site
would look like this:

```javascript
{
    "name": "we1s",  // A slug-ified version of the source name used as an ID.
    "title": "WhatEvery1Says",  // The full name of the source.
    "database": "chomp",  // Important to specify vs. other data streams.
    "webpage": "http://we1s.ucsb.edu"  // The "base" or "starting" URL.
}
```

There are other optional fields we can fill in as we go, but these are the ones
that are required.

Once you have a **Source**, you will need to create a **Query**. The **Query**
specifies exactly what it is we're looking for at a particular source. If we
were looking for the word "humanities" at the WE1S web site from 2014 to 2019,
for instance, we would structure our **Query** like so:

```javascript
{
    // Both the "name" and "title" fields are required. This is an artifact
    // of the WE1S manfiest. The "name" field should always be structured thus:
    // {source name}_{query string}_{start date}_{end_date}
    // Note that this results in some unfortunate data duplication, but it is
    // not very difficult to double-check occasionally or to parse whenever
    // changes are made.
    "name": "we1s_humanities_01-01-2014_12-31-2019",
    "title": "we1s_humanities_01-01-2014_12-31-2019",
    "query_str": "humanities",
    "start_date": "01-01-2014",
    "end_date": "12-31-2019"
}
```

Once again, there are other optional fields we can fill in as we go, but these
are the ones that are required.

The `00_import` notebook can help you create these JSON files, or you can
make them by hand or programmatically by other means. Once you have a handful
of **Source** and **Query** objects, you're ready to start scraping. Load them
into the `01_response` notebook and get started!
