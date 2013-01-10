# Airbrake Mining

A collection of python scripts to mine iOS crash reports from Airbrake.

The problem: Airbake fails for iOS projects when symbolication is
not available.

Solution: Use these scripts to:

  1. Fetch all Airbrake error reports from via their API
  2. Cluster/de-duplicate crash reports
  3. Focus on the most happening reports
  4. See affected platforms
  5. !! Symbolicate crash reports

