<!-- @@@title:Event Correlation Rule Types@@@ -->


# Event Correlation Rules


LogZilla's Event Correlation includes the following EC Rule Types:

* Single 
    - Match input event and execute an action immediately.

 
* SingleWithScript
    - Match input event and, depending on the exit value of an external script, execute an action.

* SingleWithSuppress
    - Match input event and execute an action immediately, but ignore subsequent matching events for the next `t` seconds.

* Pair
    - Match input event, execute an action immediately and ignore subsequent matching events until some other input event arrives.
    - Upon the arrival of that second event execute another action.

* PairWithWindow
    - Match input event and wait `t` seconds for some other input event to arrive.
    - If that next event is not observed within a given time window, execute an action.
    - If that next event arrives on time, execute another action.

* SingleWithThreshold
    - Count matching input events during `t` seconds
    - If the given `t` threshold is exceeded, execute an action and ignore all matching events during the rest of the specified time window.

* SingleWith2Thresholds
    - Count matching input events during `t1` seconds
    - If a given threshold is exceeded, execute an action and start counting matching events again
    - If the matching event counter per `t2` seconds drops below the second threshold, execute another action.

* Suppress
    - Suppress matching input events (used to keep the events from being matched by later rules).

* Calendar
    - Execute an action only at specific times.

* Jump
    - Submit matching input events to specific ruleset(s) for further processing.

* Options
    - Set processing options for a ruleset.

