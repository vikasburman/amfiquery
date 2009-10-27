# amfiquery

`amfiquery` is simple utility for anyone investing in Indian Mutual
Funds, and who interested in tracking their Net Asset Values. 

It basically periodically reads and parses
<http://www.amfiindia.com/spages/NAV0.txt>, and provides an API to query
the current NAV of any mutual fund you're interested in.

Just hit the URL:

<http://amfiquery.appspot.com/nav?code=105628>

to get the NAV of the fund with that scheme code. That URL is for `SBI
MAGNUM TAXGAIN SCHEME 1993 - GROWTH`, for example.

Todos:

 - A simple method to get mutual fund meta-info that I'm storing (name,
   NAV, repurchase price, sale price, etc).
 - A method to lookup/list mutual fund scheme codes.
 - Maybe even capture historical information? Right now I'm just storing
   the latest available NAV.

The application runs on the Google App Engine, and is open-source (under
the GPL v3 license). I had created this application for my own personal
use (and as a sort of experiment). Use it at your own risk. 


— Ankit Solanki • <http://ankitsolanki.com/> • <http://simulacra.in>
