# CHANGELOG

## 2.6.0
* Support for 0.9.x release of InfluxDB (contributed by @rberger)

## 2.5.0
* Move influxdb resource actions to an attribute (contributed by
  @directionless)

## 2.4.0
* Update default config for 0.8.5 and up (contributed by @tjwallace)

## 2.3.0
* Update checksums for 0.8.6 (contributed by @tjwallace)

## 2.2.2
* Touch logfile if it does not exist (contributed by @odolbeau)

## 2.2.1
* Updated `latest` checksum to be accurate (contributed by @nomadium)

## 2.2.0
* Added `dbadmin` parameter to `influxdb_user`, allowing granular control of
  which users are admins for which databases (contributed by @BarthV)

## 2.1.1
* User and admin deletion now idempotent (contributed by @flowboard)

## 2.1.0
* Multiple style and testing updates (contribued by @odolbeau)

## 2.0.4
* Default logfile path is now the Debian package default (contributed by
  @masarakki)

## 2.0.3
* Fixed typo in cluster admin check per InfluxDB 0.6.0 (contributed by @Chelo)
