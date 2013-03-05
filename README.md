# Airbrake Summary

A collection of python scripts to mine iOS crash reports from Airbrake.

The problem: Airbake fails for iOS projects when symbolication is
not available.

Solution: Use these scripts to:


## Usage

  1. Copy `config.json.sample` to `config.json` and adjust values
  2. `make fetch` -- Will fetch all the errors from Airbrake and create `errors.json`
  3. `make cluster` -- Will use the patterns from `config.json` and create `clusters.json`
