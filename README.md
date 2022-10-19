Opbeans Android Loadgen
---

This repo contains 2 scripts:

* `app-uploader` - Compiles the main branches of [opbeans-android](https://github.com/elastic/opbeans-android) and
  also [apm-agent-android](https://github.com/elastic/apm-agent-android) and uploads the opbeans-android binaries to
  Saucelabs for later use.
* `load-generator` - Fetches the latest opbeans binaries available in Saucelabs and runs the
  opbeans [Espresso](https://developer.android.com/training/testing/espresso) tests which will generate data for the apm
  endpoint provided on `app-uploader` in one of its Dockerfile `ARG`s.

Both scripts have their own Dockerfile to set the env up before running them, make sure to checkout their `ARG`s in
order to make sure you're passing them all when building the images.

There's a GitHub action in place that runs the `load-generator` every 10 minutes.