from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

from google.appengine.api.labs import taskqueue
from models import MFInfo
from google.appengine.ext import db

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("""AMFI Mutual Fund current NAV Query
Usage:
 - http://amfiquery.appspot.com/nav?code=108145 Get NAV of a fund
        """)

class NavHandler(webapp.RequestHandler):
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
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class WorkerForNAV(webapp.RequestHandler):
    def post(self):
        quotes = self.request.get('quote')
        for quote in quotes.split('\n'):
            self.save_quote(quote)

    def save_quote(self, quote):
        cols = quote.split(';')
        if len(cols) != 6:
            return

        scheme_code = cols[0]
        scheme_name = cols[1]
        nav = cols[2]
        repurchase_price = cols[3]
        sale_price = cols[4]
        date = cols[5]

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
    def get(self):

        url = 'http://www.amfiindia.com/spages/NAV0.txt'
        result = urlfetch.fetch(url)
        
        if result.status_code != 200:
            self.response.out.write('Error')
            return

        lines = result.content.split('\n')

        quotes = [line for line in lines[1:] if line.find(';') != -1]

        for chunk in chunker(quotes, 50):
            taskqueue.add(url='/tasks/worker', params={'quote': '\n'.join(chunk)})
            

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/nav', NavHandler),
                                      ('/tasks/update', UpdateNAV),
                                      ('/tasks/worker', WorkerForNAV)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
