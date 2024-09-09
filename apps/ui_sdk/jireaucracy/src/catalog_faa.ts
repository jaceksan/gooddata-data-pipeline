/* eslint-disable */
/* THIS FILE WAS AUTO-GENERATED USING CATALOG EXPORTER; YOU SHOULD NOT EDIT THIS FILE; GENERATE TIME: 2024-05-21T08:51:48.223Z; */
// @ts-ignore ignore unused imports here if they happen (e.g. when there is no measure in the workspace)
import { newAttribute, newMeasure, IAttribute, IMeasure, IMeasureDefinition, idRef } from "@gooddata/sdk-model";

/**
 * Attribute Title: Aircraft model code
 * Attribute ID: aircraft_model_code
 */
export const AircraftModelCode: IAttribute = newAttribute("aircraft_model_code");
/**
 * Attribute Title: Cancelled
 * Attribute ID: cancelled
 */
export const Cancelled: IAttribute = newAttribute("cancelled");
/**
 * Attribute Title: Code
 * Attribute ID: code
 */
export const Code: IAttribute = newAttribute("code");
/**
 * Attribute Title: Code (destination)
 * Attribute ID: code_destination
 */
export const CodeDestination = {
  /**
   * Display Form Title: Longitude (destination)
   * Display Form ID: longitude_destination
   */
  LongitudeDestination: newAttribute("longitude_destination")
  /**
   * Display Form Title: Latitude (destination)
   * Display Form ID: latitude_destination
   */,
  LatitudeDestination: newAttribute("latitude_destination")
  /**
   * Display Form Title: Code (destination)
   * Display Form ID: code_destination
   */,
  Default: newAttribute("code_destination"),
};
/**
 * Attribute Title: Code (origin)
 * Attribute ID: code_origin
 */
export const CodeOrigin = {
  /**
   * Display Form Title: Latitude (origin)
   * Display Form ID: latitude_origin
   */
  LatitudeOrigin: newAttribute("latitude_origin")
  /**
   * Display Form Title: Code (origin)
   * Display Form ID: code_origin
   */,
  Default: newAttribute("code_origin")
  /**
   * Display Form Title: Longitude (origin)
   * Display Form ID: longitude_origin
   */,
  LongitudeOrigin: newAttribute("longitude_origin"),
};
/**
 * Attribute Title: Diverted
 * Attribute ID: diverted
 */
export const Diverted: IAttribute = newAttribute("diverted");
/**
 * Attribute Title: Faa region (destination)
 * Attribute ID: faa_region_destination
 */
export const FaaRegionDestination: IAttribute = newAttribute("faa_region_destination");
/**
 * Attribute Title: Faa region (origin)
 * Attribute ID: faa_region_origin
 */
export const FaaRegionOrigin: IAttribute = newAttribute("faa_region_origin");
/**
 * Attribute Title: Fac type (destination)
 * Attribute ID: fac_type_destination
 */
export const FacTypeDestination: IAttribute = newAttribute("fac_type_destination");
/**
 * Attribute Title: Fac type (origin)
 * Attribute ID: fac_type_origin
 */
export const FacTypeOrigin: IAttribute = newAttribute("fac_type_origin");
/**
 * Attribute Title: Flight num
 * Attribute ID: flight_num
 */
export const FlightNum: IAttribute = newAttribute("flight_num");
/**
 * Attribute Title: Id2
 * Attribute ID: id2
 */
export const Id2: IAttribute = newAttribute("id2");
/**
 * Attribute Title: Manufacturer
 * Attribute ID: manufacturer
 */
export const Manufacturer: IAttribute = newAttribute("manufacturer");
/**
 * Attribute Title: Name
 * Attribute ID: name
 */
export const Name: IAttribute = newAttribute("name");
/**
 * Attribute Title: Name (destination)
 * Attribute ID: name_destination
 */
export const NameDestination: IAttribute = newAttribute("name_destination");
/**
 * Attribute Title: Name (origin)
 * Attribute ID: name_origin
 */
export const NameOrigin: IAttribute = newAttribute("name_origin");
/**
 * Attribute Title: Nickname
 * Attribute ID: nickname
 */
export const Nickname: IAttribute = newAttribute("nickname");
/**
 * Attribute Title: State (destination)
 * Attribute ID: state_destination
 */
export const StateDestination: IAttribute = newAttribute("state_destination");
/**
 * Attribute Title: State (origin)
 * Attribute ID: state_origin
 */
export const StateOrigin: IAttribute = newAttribute("state_origin");
/**
 * Attribute Title: Tail num
 * Attribute ID: tail_num
 */
export const TailNum: IAttribute = newAttribute("tail_num");
/**
 * Metric Title: Aircraft count
 * Metric ID: aircraft_count
 * Metric Type: MAQL Metric
 */
export const AircraftCount: IMeasure<IMeasureDefinition> = newMeasure(idRef("aircraft_count", "measure"));
/**
 * Metric Title: Airport count
 * Metric ID: airport_count
 * Metric Type: MAQL Metric
 */
export const AirportCount: IMeasure<IMeasureDefinition> = newMeasure(idRef("airport_count", "measure"));
/**
 * Metric Title: Avg Departure Delay
 * Metric ID: avg_departure_delay
 * Metric Type: MAQL Metric
 */
export const AvgDepartureDelay: IMeasure<IMeasureDefinition> = newMeasure(idRef("avg_departure_delay", "measure"));
/**
 * Metric Title: Avg elevation
 * Metric ID: avg_elevation
 * Metric Type: MAQL Metric
 */
export const AvgElevation: IMeasure<IMeasureDefinition> = newMeasure(idRef("avg_elevation", "measure"));
/**
 * Metric Title: Carrier count
 * Metric ID: carrier_count
 * Metric Type: MAQL Metric
 */
export const CarrierCount: IMeasure<IMeasureDefinition> = newMeasure(idRef("carrier_count", "measure"));
/**
 * Metric Title: Complex metric example
 * Metric ID: complex_metric_example
 * Metric Type: MAQL Metric
 */
export const ComplexMetricExample: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("complex_metric_example", "measure")
);
/**
 * Metric Title: Destination count
 * Metric ID: destination_count
 * Metric Type: MAQL Metric
 */
export const DestinationCount: IMeasure<IMeasureDefinition> = newMeasure(idRef("destination_count", "measure"));
/**
 * Metric Title: Flight count
 * Metric ID: flight_count
 * Metric Type: MAQL Metric
 */
export const FlightCount: IMeasure<IMeasureDefinition> = newMeasure(idRef("flight_count", "measure"));
/**
 * Metric Title: Flight count - carriers
 * Metric ID: flight_count_-_carriers
 * Metric Type: MAQL Metric
 */
export const FlightCountCarriers: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("flight_count_-_carriers", "measure")
);
/**
 * Metric Title: Flight count - destination
 * Metric ID: flight_count_-_destination
 * Metric Type: MAQL Metric
 */
export const FlightCountDestination: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("flight_count_-_destination", "measure")
);
/**
 * Metric Title: Flight count - overall
 * Metric ID: flight_count_-_overall
 * Metric Type: MAQL Metric
 */
export const FlightCountOverall: IMeasure<IMeasureDefinition> = newMeasure(idRef("flight_count_-_overall", "measure"));
/**
 * Metric Title: Flight count - TOP(X)
 * Metric ID: flight_count_-_top_x
 * Metric Type: MAQL Metric
 */
export const FlightCountTOPX: IMeasure<IMeasureDefinition> = newMeasure(idRef("flight_count_-_top_x", "measure"));
/**
 * Metric Title: Origin count
 * Metric ID: origin_count
 * Metric Type: MAQL Metric
 */
export const OriginCount: IMeasure<IMeasureDefinition> = newMeasure(idRef("origin_count", "measure"));
/**
 * Metric Title: Percentage of carrier flights
 * Metric ID: percentage_of_carrier_flights
 * Metric Type: MAQL Metric
 */
export const PercentageOfCarrierFlights: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("percentage_of_carrier_flights", "measure")
);
/**
 * Metric Title: Percentage of carrier to destination flights
 * Metric ID: percentage_of_carrier_to_destination_flights
 * Metric Type: MAQL Metric
 */
export const PercentageOfCarrierToDestinationFlights: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("percentage_of_carrier_to_destination_flights", "measure")
);
/**
 * Metric Title: Percentage of current to carrier
 * Metric ID: percentage_of_current_to_carrier
 * Metric Type: MAQL Metric
 */
export const PercentageOfCurrentToCarrier: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("percentage_of_current_to_carrier", "measure")
);
/**
 * Metric Title: Percentage of flights
 * Metric ID: percentage_of_flights
 * Metric Type: MAQL Metric
 */
export const PercentageOfFlights: IMeasure<IMeasureDefinition> = newMeasure(idRef("percentage_of_flights", "measure"));
/**
 * Metric Title: Percentage of flights - expanded
 * Metric ID: percentage_of_flights_-_expanded
 * Metric Type: MAQL Metric
 */
export const PercentageOfFlightsExpanded: IMeasure<IMeasureDefinition> = newMeasure(
  idRef("percentage_of_flights_-_expanded", "measure")
);
/**
 * Metric Title: Total distance
 * Metric ID: total_distance
 * Metric Type: MAQL Metric
 */
export const TotalDistance: IMeasure<IMeasureDefinition> = newMeasure(idRef("total_distance", "measure"));
/**
 * Fact Title: Arr delay
 * Fact ID: arr_delay
 */
export const ArrDelay = {
  /**
   * Fact Title: Arr delay
   * Fact ID: arr_delay
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("arr_delay", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Arr delay
   * Fact ID: arr_delay
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("arr_delay", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Arr delay
   * Fact ID: arr_delay
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("arr_delay", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Arr delay
   * Fact ID: arr_delay
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("arr_delay", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Arr delay
   * Fact ID: arr_delay
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("arr_delay", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Arr delay
   * Fact ID: arr_delay
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("arr_delay", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Dep delay
 * Fact ID: dep_delay
 */
export const DepDelay = {
  /**
   * Fact Title: Dep delay
   * Fact ID: dep_delay
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("dep_delay", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Dep delay
   * Fact ID: dep_delay
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("dep_delay", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Dep delay
   * Fact ID: dep_delay
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("dep_delay", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Dep delay
   * Fact ID: dep_delay
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("dep_delay", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Dep delay
   * Fact ID: dep_delay
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("dep_delay", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Dep delay
   * Fact ID: dep_delay
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("dep_delay", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Distance
 * Fact ID: distance
 */
export const Distance = {
  /**
   * Fact Title: Distance
   * Fact ID: distance
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("distance", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Distance
   * Fact ID: distance
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("distance", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Distance
   * Fact ID: distance
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("distance", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Distance
   * Fact ID: distance
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("distance", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Distance
   * Fact ID: distance
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("distance", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Distance
   * Fact ID: distance
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("distance", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Elevation (destination)
 * Fact ID: elevation_destination
 */
export const ElevationDestination = {
  /**
   * Fact Title: Elevation (destination)
   * Fact ID: elevation_destination
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("elevation_destination", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Elevation (destination)
   * Fact ID: elevation_destination
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("elevation_destination", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Elevation (destination)
   * Fact ID: elevation_destination
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("elevation_destination", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Elevation (destination)
   * Fact ID: elevation_destination
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("elevation_destination", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Elevation (destination)
   * Fact ID: elevation_destination
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("elevation_destination", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Elevation (destination)
   * Fact ID: elevation_destination
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("elevation_destination", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Elevation (origin)
 * Fact ID: elevation_origin
 */
export const ElevationOrigin = {
  /**
   * Fact Title: Elevation (origin)
   * Fact ID: elevation_origin
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("elevation_origin", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Elevation (origin)
   * Fact ID: elevation_origin
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("elevation_origin", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Elevation (origin)
   * Fact ID: elevation_origin
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("elevation_origin", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Elevation (origin)
   * Fact ID: elevation_origin
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("elevation_origin", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Elevation (origin)
   * Fact ID: elevation_origin
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("elevation_origin", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Elevation (origin)
   * Fact ID: elevation_origin
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("elevation_origin", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Flight time
 * Fact ID: flight_time
 */
export const FlightTime = {
  /**
   * Fact Title: Flight time
   * Fact ID: flight_time
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("flight_time", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Flight time
   * Fact ID: flight_time
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("flight_time", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Flight time
   * Fact ID: flight_time
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("flight_time", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Flight time
   * Fact ID: flight_time
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("flight_time", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Flight time
   * Fact ID: flight_time
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("flight_time", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Flight time
   * Fact ID: flight_time
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("flight_time", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Seats
 * Fact ID: seats
 */
export const Seats = {
  /**
   * Fact Title: Seats
   * Fact ID: seats
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("seats", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Seats
   * Fact ID: seats
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("seats", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Seats
   * Fact ID: seats
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("seats", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Seats
   * Fact ID: seats
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("seats", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Seats
   * Fact ID: seats
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("seats", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Seats
   * Fact ID: seats
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("seats", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Taxi in
 * Fact ID: taxi_in
 */
export const TaxiIn = {
  /**
   * Fact Title: Taxi in
   * Fact ID: taxi_in
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("taxi_in", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Taxi in
   * Fact ID: taxi_in
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("taxi_in", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Taxi in
   * Fact ID: taxi_in
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("taxi_in", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Taxi in
   * Fact ID: taxi_in
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("taxi_in", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Taxi in
   * Fact ID: taxi_in
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("taxi_in", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Taxi in
   * Fact ID: taxi_in
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("taxi_in", "fact"), (m) => m.aggregation("runsum")),
};
/**
 * Fact Title: Taxi out
 * Fact ID: taxi_out
 */
export const TaxiOut = {
  /**
   * Fact Title: Taxi out
   * Fact ID: taxi_out
   * Fact Aggregation: sum
   */
  Sum: newMeasure(idRef("taxi_out", "fact"), (m) => m.aggregation("sum"))
  /**
   * Fact Title: Taxi out
   * Fact ID: taxi_out
   * Fact Aggregation: avg
   */,
  Avg: newMeasure(idRef("taxi_out", "fact"), (m) => m.aggregation("avg"))
  /**
   * Fact Title: Taxi out
   * Fact ID: taxi_out
   * Fact Aggregation: min
   */,
  Min: newMeasure(idRef("taxi_out", "fact"), (m) => m.aggregation("min"))
  /**
   * Fact Title: Taxi out
   * Fact ID: taxi_out
   * Fact Aggregation: max
   */,
  Max: newMeasure(idRef("taxi_out", "fact"), (m) => m.aggregation("max"))
  /**
   * Fact Title: Taxi out
   * Fact ID: taxi_out
   * Fact Aggregation: median
   */,
  Median: newMeasure(idRef("taxi_out", "fact"), (m) => m.aggregation("median"))
  /**
   * Fact Title: Taxi out
   * Fact ID: taxi_out
   * Fact Aggregation: runsum
   */,
  Runsum: newMeasure(idRef("taxi_out", "fact"), (m) => m.aggregation("runsum")),
};
/** Available Date Data Sets */
export const DateDatasets = {
  /**
   * Date Data Set Title: Departure time
   * Date Data Set ID: dep_time
   */
  DepartureTime: {
    ref: idRef("dep_time", "dataSet"),
    identifier: "dep_time"
    /**
     * Date Attribute: Departure time - Date
     * Date Attribute ID: dep_time.day
     */,
    DepartureTimeDate: {
      ref: idRef("dep_time.day", "attribute"),
      identifier: "dep_time.day"
      /**
       * Display Form Title: Departure time - Date
       * Display Form ID: dep_time.day
       */,
      Default: newAttribute("dep_time.day"),
    }
    /**
     * Date Attribute: Departure time - Day of Month
     * Date Attribute ID: dep_time.dayOfMonth
     */,
    DepartureTimeDayOfMonth: {
      ref: idRef("dep_time.dayOfMonth", "attribute"),
      identifier: "dep_time.dayOfMonth"
      /**
       * Display Form Title: Departure time - Day of Month
       * Display Form ID: dep_time.dayOfMonth
       */,
      Default: newAttribute("dep_time.dayOfMonth"),
    }
    /**
     * Date Attribute: Departure time - Day of Week
     * Date Attribute ID: dep_time.dayOfWeek
     */,
    DepartureTimeDayOfWeek: {
      ref: idRef("dep_time.dayOfWeek", "attribute"),
      identifier: "dep_time.dayOfWeek"
      /**
       * Display Form Title: Departure time - Day of Week
       * Display Form ID: dep_time.dayOfWeek
       */,
      Default: newAttribute("dep_time.dayOfWeek"),
    }
    /**
     * Date Attribute: Departure time - Day of Year
     * Date Attribute ID: dep_time.dayOfYear
     */,
    DepartureTimeDayOfYear: {
      ref: idRef("dep_time.dayOfYear", "attribute"),
      identifier: "dep_time.dayOfYear"
      /**
       * Display Form Title: Departure time - Day of Year
       * Display Form ID: dep_time.dayOfYear
       */,
      Default: newAttribute("dep_time.dayOfYear"),
    }
    /**
     * Date Attribute: Departure time - Hour
     * Date Attribute ID: dep_time.hour
     */,
    DepartureTimeHour: {
      ref: idRef("dep_time.hour", "attribute"),
      identifier: "dep_time.hour"
      /**
       * Display Form Title: Departure time - Hour
       * Display Form ID: dep_time.hour
       */,
      Default: newAttribute("dep_time.hour"),
    }
    /**
     * Date Attribute: Departure time - Hour of Day
     * Date Attribute ID: dep_time.hourOfDay
     */,
    DepartureTimeHourOfDay: {
      ref: idRef("dep_time.hourOfDay", "attribute"),
      identifier: "dep_time.hourOfDay"
      /**
       * Display Form Title: Departure time - Hour of Day
       * Display Form ID: dep_time.hourOfDay
       */,
      Default: newAttribute("dep_time.hourOfDay"),
    }
    /**
     * Date Attribute: Departure time - Minute
     * Date Attribute ID: dep_time.minute
     */,
    DepartureTimeMinute: {
      ref: idRef("dep_time.minute", "attribute"),
      identifier: "dep_time.minute"
      /**
       * Display Form Title: Departure time - Minute
       * Display Form ID: dep_time.minute
       */,
      Default: newAttribute("dep_time.minute"),
    }
    /**
     * Date Attribute: Departure time - Minute of Hour
     * Date Attribute ID: dep_time.minuteOfHour
     */,
    DepartureTimeMinuteOfHour: {
      ref: idRef("dep_time.minuteOfHour", "attribute"),
      identifier: "dep_time.minuteOfHour"
      /**
       * Display Form Title: Departure time - Minute of Hour
       * Display Form ID: dep_time.minuteOfHour
       */,
      Default: newAttribute("dep_time.minuteOfHour"),
    }
    /**
     * Date Attribute: Departure time - Month/Year
     * Date Attribute ID: dep_time.month
     */,
    DepartureTimeMonthYear: {
      ref: idRef("dep_time.month", "attribute"),
      identifier: "dep_time.month"
      /**
       * Display Form Title: Departure time - Month/Year
       * Display Form ID: dep_time.month
       */,
      Default: newAttribute("dep_time.month"),
    }
    /**
     * Date Attribute: Departure time - Month of Year
     * Date Attribute ID: dep_time.monthOfYear
     */,
    DepartureTimeMonthOfYear: {
      ref: idRef("dep_time.monthOfYear", "attribute"),
      identifier: "dep_time.monthOfYear"
      /**
       * Display Form Title: Departure time - Month of Year
       * Display Form ID: dep_time.monthOfYear
       */,
      Default: newAttribute("dep_time.monthOfYear"),
    }
    /**
     * Date Attribute: Departure time - Quarter/Year
     * Date Attribute ID: dep_time.quarter
     */,
    DepartureTimeQuarterYear: {
      ref: idRef("dep_time.quarter", "attribute"),
      identifier: "dep_time.quarter"
      /**
       * Display Form Title: Departure time - Quarter/Year
       * Display Form ID: dep_time.quarter
       */,
      Default: newAttribute("dep_time.quarter"),
    }
    /**
     * Date Attribute: Departure time - Quarter of Year
     * Date Attribute ID: dep_time.quarterOfYear
     */,
    DepartureTimeQuarterOfYear: {
      ref: idRef("dep_time.quarterOfYear", "attribute"),
      identifier: "dep_time.quarterOfYear"
      /**
       * Display Form Title: Departure time - Quarter of Year
       * Display Form ID: dep_time.quarterOfYear
       */,
      Default: newAttribute("dep_time.quarterOfYear"),
    }
    /**
     * Date Attribute: Departure time - Week/Year
     * Date Attribute ID: dep_time.week
     */,
    DepartureTimeWeekYear: {
      ref: idRef("dep_time.week", "attribute"),
      identifier: "dep_time.week"
      /**
       * Display Form Title: Departure time - Week/Year
       * Display Form ID: dep_time.week
       */,
      Default: newAttribute("dep_time.week"),
    }
    /**
     * Date Attribute: Departure time - Week of Year
     * Date Attribute ID: dep_time.weekOfYear
     */,
    DepartureTimeWeekOfYear: {
      ref: idRef("dep_time.weekOfYear", "attribute"),
      identifier: "dep_time.weekOfYear"
      /**
       * Display Form Title: Departure time - Week of Year
       * Display Form ID: dep_time.weekOfYear
       */,
      Default: newAttribute("dep_time.weekOfYear"),
    }
    /**
     * Date Attribute: Departure time - Year
     * Date Attribute ID: dep_time.year
     */,
    DepartureTimeYear: {
      ref: idRef("dep_time.year", "attribute"),
      identifier: "dep_time.year"
      /**
       * Display Form Title: Departure time - Year
       * Display Form ID: dep_time.year
       */,
      Default: newAttribute("dep_time.year"),
    },
  },
};
export const Insights = {
  /**
   * Insight Title: Airports - by facility type
   * Insight ID: airports_by_facility_type
   */
  AirportsByFacilityType: "airports_by_facility_type"
  /**
   * Insight Title: Airports - by region, state and facility type
   * Insight ID: airports_by_region_state_facility_type
   */,
  AirportsByRegionStateAndFacilityType: "airports_by_region_state_facility_type"
  /**
   * Insight Title: Airports - by state
   * Insight ID: airports_by_state
   */,
  AirportsByState: "airports_by_state"
  /**
   * Insight Title: Carriers - overview
   * Insight ID: carriers_overview
   */,
  CarriersOverview: "carriers_overview"
  /**
   * Insight Title: Flights - by carrier
   * Insight ID: flights_by_carrier
   */,
  FlightsByCarrier: "flights_by_carrier"
  /**
   * Insight Title: Flights - by month
   * Insight ID: flights_by_month
   */,
  FlightsByMonth: "flights_by_month"
  /**
   * Insight Title: Flights - by origin
   * Insight ID: flights_by_origin
   */,
  FlightsByOrigin: "flights_by_origin"
  /**
   * Insight Title: Flight stats in time
   * Insight ID: flight_stats_in_time
   */,
  FlightStatsInTime: "flight_stats_in_time"
  /**
   * Insight Title: Flight stats in time v2
   * Insight ID: flight_stats_in_time_v2
   */,
  FlightStatsInTimeV2: "flight_stats_in_time_v2"
  /**
   * Insight Title: Geo - flight count and departure delay by airport
   * Insight ID: geo_flight_count_and_departure_delay_by_airport
   */,
  GeoFlightCountAndDepartureDelayByAirport: "geo_flight_count_and_departure_delay_by_airport"
  /**
   * Insight Title: Pivoting Example - Table
   * Insight ID: pivoting_example_table
   */,
  PivotingExampleTable: "pivoting_example_table"
  /**
   * Insight Title: Pivoting Example - TreeMap
   * Insight ID: pivoting_example_treemap
   */,
  PivotingExampleTreeMap: "pivoting_example_treemap"
  /**
   * Insight Title: Time - Carriers over time
   * Insight ID: time_carriers_over_time
   */,
  TimeCarriersOverTime: "time_carriers_over_time",
};
export const Dashboards = {
  /**
   * Dashboard Title: 01 - Airports
   * Dashboard ID: airports
   */
  _01Airports: "airports"
  /**
   * Dashboard Title: 03 - Carriers
   * Dashboard ID: carriers
   */,
  _03Carriers: "carriers"
  /**
   * Dashboard Title: 02 - Flights
   * Dashboard ID: flights
   */,
  _02Flights: "flights",
};
