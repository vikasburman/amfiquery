# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

from google.appengine.api import taskqueue
from models import MFInfo
from google.appengine.ext import db


class MainPage(webapp.RequestHandler):
    """ Main page handler, redirect to index.html """
    def get(self):
        self.redirect('/index.html')

class NavHandler(webapp.RequestHandler):
    """ The handler that serves the NAV prices for each fund.
    We just need to lookup the fund in the datastore, and output its
    current NAV.
    """
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        code = self.request.get('code')

        if code == '' or code == None:
            self.response.out.write('error')
            return

        query = db.GqlQuery('SELECT * FROM MFInfo WHERE scheme_code = :code', code=code)
        result = query.fetch(1)

        if len(result) == 0:
            self.response.out.write('error')
            return

        self.response.out.write(result[0].nav)

def chunker(seq, size):
    """ Utility method to split a list into chunks.
    See: http://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks/434328#434328"""
    return [seq[pos:pos + size] for pos in xrange(0, len(seq), size)]

class WorkerForNAV(webapp.RequestHandler):
    """ The task queue handler. It received chunks of quotes (50 each).
    It takes each quote individually, and stores/updates it in the
    datastore.
    """

    def post(self):
        quotes = self.request.get('quote')
        for quote in quotes.split('\n'):
            self.save_quote(quote)

    def save_quote(self, quote):
        cols = quote.split(';')
        if len(cols) != 8:
            logging.error("Quote is not in proper format: " + quote)
            return

        scheme_code = cols[0]
        scheme_name = cols[3]
        nav = cols[4]
        repurchase_price = cols[5]
        sale_price = cols[6]
        date = cols[7]

        query = db.GqlQuery('SELECT * FROM MFInfo WHERE scheme_code = :code', code=scheme_code)
        result = query.fetch(1)

        if len(result) == 0:
            mf_quote = MFInfo(scheme_code = scheme_code,
                              scheme_name = scheme_name,
                              nav = nav,
                              repurchase_price = repurchase_price,
                              sale_price = sale_price,
                              date = date)

        else:
            mf_quote = result[0]
            mf_quote.scheme_name = scheme_name
            mf_quote.nav = nav
            mf_quote.repurchase_price = repurchase_price
            mf_quote.sale_price = sale_price
            mf_quote.date = date

        mf_quote.put()


class UpdateNAV(webapp.RequestHandler):
    """ This is the handler called daily via a cron job.
    We:
      - Fetch http://portal.amfiindia.com/spages/NAV0.txt
      - Parse it
      - Split it into chunks with 50 quotes each
      - Put each chunk on the default task queue
    """
    def get(self):

        url = 'http://portal.amfiindia.com/spages/NAV0.txt'
        result = urlfetch.fetch(url, deadline=120)

        if result.status_code != 200:
            self.response.out.write('Error')
            return

        lines = result.content.split('\n')

        quotes = [line for line in lines[1:] if line.find(';') != -1]

        for chunk in chunker(quotes, 50):
          taskqueue.add(url='/tasks/worker', params={'quote': '\n'.join(chunk)})


application = webapp.WSGIApplication(
    [('/', MainPage),                  # Home page
     ('/nav', NavHandler),             # Handler for finding current NAV
     ('/tasks/update', UpdateNAV),     # Cron job
     ('/tasks/worker', WorkerForNAV)], # Task queue worker
    debug=False)

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
