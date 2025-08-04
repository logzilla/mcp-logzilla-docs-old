<!-- @@@title:Lua Rules Tutorial@@@ -->

# LogZilla Rules

LogZilla Rules are how LogZilla can parse and rewrite log messages to extract
the specific bits of useful information, as well as to rewrite the log message
so that when you review the log messages the information shown is more useful
to you. There are two types of LogZilla rules: rewrite rules, which are defined
through simple `JSON`, `YAML`, or `LUA` rules, which are very powerful
but are defined in lua programming language files. Both types of rules can be
used at the same time, but be aware that lua rules are executed before rewrite
rules, so that any data modifications or other actions taken by the lua rules
will precede the execution of the rewrite rules.

# Lua Rules

<iframe style="display: block; margin-left: auto; margin-right: auto;" width="560" height="315" src="https://www.youtube.com/embed/YdF97GZbwQI" title="LogZilla University | Lua Rules Tutorial" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>

LogZilla’s powerful Lua rules open up a world of possibilities for
customizing the way your network events are processed. By harnessing the
flexibility of the Lua scripting language, you can create sophisticated
rules tailored to your specific needs. Lua’s simplicity and versatility
have made it a popular choice for application customization, and its
integration with LogZilla enables you to take your event management to
the next level.

The use of LPEG (Lua Parsing Expression Grammar) within LogZilla Lua
rules offers a more efficient approach to pattern matching compared to
traditional regular expressions. LPEG allows for faster event processing
rates (EPS), ensuring that your LogZilla system can handle large volumes
of data without sacrificing performance. This not only streamlines your
network event management but also helps to optimize your overall system
resources.

Creating LogZilla rules with Lua involves defining specific Lua
functions and applying them to your LogZilla rules. This process enables
you to achieve greater control over your network event management,
giving you the power to create custom solutions that address your unique
challenges. With LogZilla’s Lua rules, you can tailor your event
processing to suit the specific requirements of your network
infrastructure.

LogZilla’s implementation of Lua rules revolves around several
fundamental concepts. In the following sections, we will delve deeper
into these ideas.

Although Lua does support regular expressions, it is not advised to
utilize them in this context. As an alternative, it is recommended to
employ LPEG (Lua Parsing Expression Grammar), a more efficient
pattern-matching technique specific to Lua. LPEG significantly enhances
event processing rates (EPS or events-per-second) for LogZilla.

You can find practical examples of these files in the subsequent
“Examples” section.

## Implementing and Testing LogZilla Lua Rules

LogZilla requires two files for Lua “rewrite” rules: one containing
the Lua logic for rule processing and another containing rule tests.
The key element of the Lua rule file is a *process* function, that
runs on every incoming log message.  The key elements of the tests
file are one or more individual tests, consisting of the data
describing the incoming log event, and then the event data that
would result from processing the rule.  The tests file is mandatory,
because it is critical in verifying that the rule behavior is as desired.

Name these files similarly, such as `123-ruletitle.lua` for the Lua rule file and `123-ruletitle.tests.yaml` for the tests file (e.g., `123-mswindows.lua` and `123-mswindows.tests.yaml`).

The Lua rule file is a plain text file containing only valid Lua code,
while the tests file is a YAML text file describing a sample incoming
log event and the expected event data after Lua rule processing.

A simple example demonstrates replacing the `program` field value of an
incoming event with `Unknown`. It’s recommended to write the tests file
before the rule file to clarify the input and processing the rule must
handle.

When loading a new rule or testing it, LogZilla first verifies the Lua
rule file’s validity, executes the `process` function within the Lua
code, and provides the `event` function argument data as detailed in the
tests file. LogZilla compares the modified `event` argument data with
the tests file data, and if they match, the test is successful.

Tests files are written in [YAML](https://yaml.org/). The required
structure for the tests file is to begin with a `TEST_CASES` list of
objects, each of which is a single test case. Each test case consists
of two objects, the `event` describing what data would be in the 
incoming event, and the `expect`, which indicates what the resultant
event data would be after the rule runs.

For more complex cases involving `extra_fields` (for JSON data) and
`user_tags` (for user tags set by the rule), the elements are followed
by indented lines with sub-fields or elements of that dictionary.

In this straightforward example, the test file in valid YAML format
appears as follows:

    TEST_CASES:
    - event:
        program: "-"
      expect:
        program: Unknown

This indicates that when the `program` field of a log event is `-`, the
expected outcome after rule processing is for the `program` field to be
`Unknown`.

The Lua rule must include a function called `process` that takes a
single argument, typically named `event`. This function is executed once
for every log event encountered by LogZilla, with the log event as the
`event` function argument.

Considering the desired operation specified in the test file above, the
corresponding rule file is:

    function process(event)
        event.program = 'Unknown'
    end

This Lua rule examines the `program` field of the log event. In all
cases, the rule modifies the field to `Unknown`. This would not be
a useful rule, it is just for demonstration purposes.

This rule and its accompanying test file are now prepared for use and
can be checked for accuracy and validity. You can do this by using the
`logzilla rules test --path` command-line utility, as demonstrated
below:

    $ logzilla rules test --path tut1.lua
    ================================== test session starts ==================================
    platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /tmp
    collected 1 item

    tut1.tests.yaml::test_case_1 PASSED                                              [100%]

    ================================== 1 passed in 0.02s ===================================

Upon executing the `rules test` command, LogZilla successfully validates
the Lua code and confirms that the rule functions as expected.

To demonstrate a *failure* in verifying the results of rule processing,
you can modify the tests as follows (so that the rule’s execution will
not yield the indicated test result):

    TEST_CASES:
    - event:
        program: "-"
      expect:
        program: Unknown
    - event:
        program: syslog
      expect:
        program: syslog

Now, when you run `logzilla rules test --path tut1.lua`, you’ll receive
the following result:

    $ logzilla rules test --path tut1.lua
    ================================== test session starts ==================================
    platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /tmp
    collected 2 items

    tut1.tests.yaml::test_case_1 PASSED                                              [ 50%]
    tut1.tests.yaml::test_case_2 FAILED                                              [100%]

    ======================================= FAILURES =======================================
    _____________________________ tut1.tests.yaml::test_case_2 _____________________________
    Failed test at /tmp/tut1.tests.yaml:6:
    - event:
        program: syslog
      expect:
        program: syslog

    Event before:
    cisco_mnemonic: ''
    counter: 1
    facility: 0
    first_occurrence: 1617280957288796
    host: ''
    id: 0
    last_occurrence: 1617280957288796
    message: Some random message
    program: syslog
    severity: 0
    status: 0
    user_tags: {}

    Event after:
    cisco_mnemonic: ''
    counter: 1
    facility: 0
    first_occurrence: 1617280957288796
    host: ''
    id: 0
    last_occurrence: 1617280957288796
    message: Some random message
    program: Unknown
    severity: 0
    status: 0
    user_tags: {}

    Error: Wrong value of program, got: "Unknown", expected: "syslog"
    ================================= short test summary info =================================
    FAILED ../../../tmp/tut1.tests.yaml::test_case_2 - Wrong value of program, got: "Unkn...
    ================================= 1 failed, 1 passed in 0.02s ==============================

This result shows that the first test was successful, but the second one
failed. The output displays the log event details before and after rule
execution, along with a detailed explanation of the discrepancies
between the expected and received results.

In this example, to adjust the rule so that the given test passes, you
can modify the rule as follows:

``` lua
function process(event)
    if event.program == '-' then
        event.program = 'Unknown'
    end
end
```

This alteration ensures that the rule only modifies the `program` field
of the event when that program field is `-`. This will make the first
test meet the condition and execute the conditional behavior, while the
second test will not meet the condition, leaving the `program` field
unchanged.

Now, when tested, the rule will pass:

    $ logzilla rules test --path tut1.lua
    ================================== test session starts ==================================
    platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /tmp
    collected 2 items

    tut1.tests.yaml::test_case_1 PASSED                                              [ 50%]
    tut1.tests.yaml::test_case_2 PASSED                                              [100%]

    ================================== 2 passed in 0.02s ===================================

At this point, you can add the rule to LogZilla:

    $ logzilla rules add tut1.lua
    Rule tut1 added and enabled
    Reloading rules ...
    Rules reloaded

You can verify the addition:

    $ logzilla rules list
    Name            Source    Type    Status
    --------------  --------  ------  --------
    600-lz-program  system    lua     enabled
    tut1            user      lua     enabled

This process should be followed when implementing new rules: create the
tests file, create the rule, test the rule, and add the rule. At this
point, the rule will be active and will run upon receipt of every log
message. If desired, you can perform further verification using the
`logzilla sender` command to process actual (predefined) log messages
and view the results in the LogZilla user interface.

## Handling Errors

There are three types of errors that can be encountered when adding new
rules to LogZilla: the rule can be invalid Lua and be unable to be
interpreted; the rule can result in a Lua execution failure while
running (a *runtime* error), or the results of rule execution do not
match the expected results as detailed in the tests file.

### Invalid Lua Errors

Invalid Lua errors are recognized when adding the rule. An example of
such an error would be:

``` lua
junction process(event)
    if event.program == '-' then
        event.program = 'Unknown'
    end
end
```

This example states `junction` rather than `function`, causing the Lua
interpreter to not understand the intent.

Now, when testing or loading the rule, the following error would be
received:

    $ logzilla rules test --path err.lua
    ================================== test session starts ==================================
    platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /tmp
    collected 1 item

    err.tests.yaml::test_case_1 ERROR                                                [100%]

    ======================================== ERRORS ========================================
    ____________________ ERROR at setup of err.tests.yaml::test_case_1 _____________________
    Error in rule /tmp/err.lua
    -> junction process(event)
           if event.program == '-' then
               event.program = 'Unknown'
           end
       end

    Error loading rule err.lua
    sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
    -------------------------------- Captured stderr setup ---------------------------------
    [sol3] An error occurred and has been passed to an error handler: sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
     lz.Rule    WARNING  Rule err.lua validation errors:
     lz.Rule    WARNING  ... sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
    ---------------------------------- Captured log setup ----------------------------------
    WARNING  lz.Rule:rules.py:151 Rule err.lua validation errors:
    WARNING  lz.Rule:rules.py:153 ... sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
    ================================= short test summary info ================================
    ERROR ../../../tmp/err.tests.yaml::test_case_1 - Error loading rule err.lua
    =================================== 1 error in 0.34s ===================================

This output details the location and nature of the problem:

    Error in rule /tmp/err.lua
    -> junction process(event)

shows the actual source code line with the problem, and
`sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'` details
the nature of the error (in this case, this is indicating that Lua is
interpreting `junction` as a variable declaration and is expecting it to
be followed by `=` and the variable value).

Since the rule is not valid Lua, the tests file cannot be run (to
determine if the expected results match those returned).

## Handling Errors

There are three types of errors that can be encountered when adding new
rules to LogZilla: the rule can be invalid Lua and be unable to be
interpreted; the rule can result in a Lua execution failure while
running (a *runtime* error), or the results of rule execution do not
match the expected results as detailed in the tests file.

### Invalid Lua Errors

Invalid Lua errors are recognized when adding the rule. An example of
such an error would be:

``` lua
junction process(event)
    if event.program == '-' then
        event.program = 'Unknown'
    end
end
```

This example states `junction` rather than `function`, causing the Lua
interpreter to not understand the intent.

Now, when testing or loading the rule, the following error would be
received:

    $ logzilla rules test --path err.lua
    ================================== test session starts ==================================
    platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /tmp
    collected 1 item

    err.tests.yaml::test_case_1 ERROR                                                [100%]

    ======================================== ERRORS ========================================
    ____________________ ERROR at setup of err.tests.yaml::test_case_1 _____________________
    Error in rule /tmp/err.lua
    -> junction process(event)
           if event.program == '-' then
               event.program = 'Unknown'
           end
       end

    Error loading rule err.lua
    sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
    -------------------------------- Captured stderr setup ---------------------------------
    [sol3] An error occurred and has been passed to an error handler: sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
     lz.Rule    WARNING  Rule err.lua validation errors:
     lz.Rule    WARNING  ... sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
    ---------------------------------- Captured log setup ----------------------------------
    WARNING  lz.Rule:rules.py:151 Rule err.lua validation errors:
    WARNING  lz.Rule:rules.py:153 ... sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'
    ================================= short test summary info ================================
    ERROR ../../../tmp/err.tests.yaml::test_case_1 - Error loading rule err.lua
    =================================== 1 error in 0.34s ===================================

This output details the location and nature of the problem:

    Error in rule /tmp/err.lua
    -> junction process(event)

shows the actual source code line with the problem, and
`sol: syntax error: /tmp/err.lua:1: '=' expected near 'process'` details
the nature of the error (in this case, this is indicating that Lua is
interpreting `junction` as a variable declaration and is expecting it to
be followed by `=` and the variable value).

Since the rule is not valid Lua, the tests file cannot be run (to
determine if the expected results match those returned).

### Lua Execution Errors

Lua execution errors are errors in which, although the Lua code is
syntactically and grammatically correct and is “understood” by Lua,
running the Lua rule results in an error or failure condition (before
completion).

An example of a Lua rule exhibiting this scenario:

``` lua
function process(event)
    call_some_unexistent_function()
    if event.program == '-' then
        event.program = 'Unknown'
    end
end
```

As shown, `call_some_unexistent_function()` is understood by Lua to be a
request for execution of that function, and thus is valid Lua. However,
upon execution, since no such function was defined in the rule, Lua is
unable to find and execute that function and is unable to complete
execution.

The following error would be received:

    $ logzilla rules test --path err.lua
    ================================== test session starts ==================================
    platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /tmp
    collected 1 item

    err.tests.yaml::test_case_1 FAILED                                               [100%]

    ======================================= FAILURES =======================================
    _____________________________ err.tests.yaml::test_case_1 ______________________________
    Error in rule /tmp/err.lua
       function process(event)
    ->     call_some_unexistent_function()
           if event.program == '-' then
               event.program = 'Unknown'
           end
       end

    sol: runtime error: /tmp/err.lua:2: attempt to call global 'call_some_unexistent_function' (a nil value)
    stack traceback:
        /tmp/err.lua:2: in function </tmp/err.lua:1>
    --------------------------------- Captured stderr call ---------------------------------
    2021-04-06 14:48:11.785641 lz.parser WARNING Error in LUA rule: /tmp/err.lua:2: attempt to call global 'call_some_unexistent_function' (a nil value)
    stack traceback:
        /tmp/err.lua:2: in function </tmp/err.lua:1>
    2021-04-06 14:48:11.785685 lz.parser WARNING Failure of rule err.lua
    ================================ short test summary info ================================
    FAILED ../../../tmp/err.tests.yaml::test_case_1 - sol: runtime error: /tmp/err.lua:2:...
    ================================== 1 failed in 0.02s ===================================

Like the previous example, the error text indicates the line, location,
and reason for the error, but also (for more advanced users) includes
the “stack trace” showing the (nested) function execution resulting in
the error.

### Runtime Errors That Pass Tests

In some scenarios, the rule will pass tests (including syntax/grammar,
execution, and results validation), but when used “live,” it will result
in errors.

An example scenario would be similar to the above rule with the invalid
function `call_some_unexistent_function()` but attempting to execute it
only in certain conditions (in this case, a condition not exercised by
the tests file, which reinforces the need for the tests file to check
all “types” of log messages received by the rule):

``` lua
function process(event)
    if event.program == "somespecialprogram" then
        unknown_function()
    end
    if event.program == '-' then
        event.program = 'Unknown'
    end
end
```

Because the error code was not executed during the test, this rule would
be added and would go “live.” Then in “real” operation, it could result
in errors. The fact that in-use errors are being encountered would be
revealed by listing the rules, `logzilla rules list`:

    $ logzilla rules list
    Name           Source    Type    Status    Errors
    -------------  --------  ------  --------  --------
    err            user      lua     enabled   3

This indicates that for all the events received by LogZilla (and
processed by the rule), three of those events resulted in the rule
failing.

When rules failures are encountered “live,” the details of the errors
encountered can be displayed using:

    $ logzilla rules errors err
    ======================================================================
    Rule err, 3 errors in last hour:
    ----------------------------------------------------------------------
    Time: 2021-04-20 07:50:11

    Event:
        cisco_mnemonic: ''
        counter: 1
        facility: 0
        first_occurrence: 1618905011.405836
        host: Host1
        id: 0
        last_occurrence: 1618905011.405836
        message: Message nr 1
        program: fail
        severity: 0
        status: 0
        user_tags: {}

    Error:
        /etc/logzilla/rules/user/err.lua:5: attempt to call global 'unknown_function' (a nil value)
        stack traceback:
                /etc/logzilla/rules/user/err.lua:5: in function </etc/logzilla/rules/user/err.lua:1>
    ----------------------------------------------------------------------

This provides the method for understanding the error so that it can be
corrected.

Note: For any given rule, LogZilla has a limit on the number of errors
per hour that can be encountered before the rule is automatically
disabled – by default, five errors per hour. Any rule that reaches this
limit becomes disabled and will no longer be run for each incoming log
event.

The fact that rule execution has been disabled might be noticed in that
any LogZilla display or trigger elements depending on that rule
execution cease to work. In addition, the error condition can be
manually revealed:

    $ logzilla rules list
    Name           Source    Type    Status    Errors
    -------------  --------  ------  --------  --------
    err            user      lua     disabled  5

The rule failure would also be exhibited in LogZilla logs
(`logzilla logs`):

    2021-04-20 08:01:33.186795 [parsermodule] lz.parser WARNING Failure of rule err.lua on event Event({"id":0,"severity":1,"facility":0,"message":"Message nr 2","host":"Host2","program":"fail","cisco_mnemonic":"","first_occurrence":1618905692885420,"last_occurrence":1618905692885420,"counter":1,"status":0,"user_tags":{}}):
    /etc/logzilla/rules/user/err.lua:5: attempt to call global 'unknown_function' (a nil value)
    stack traceback:
        /etc/logzilla/rules/user/err.lua:5: in function </etc/logzilla/rules/user/err.lua:1>
    2021-04-20 08:01:34.108472 [parsermodule/1] lz.ParserModule WARNING Reached limit of errors in rule err (limit: 5, errors: 5),  disabling rule.

When the rule is corrected (in this example possibly by providing the
missing `unknown_function()`), the rule can be re-added to LogZilla, to
update that rule and re-enable it: `logzilla rules add myrule.lua -f` to
add the rule, resulting in:

    $ logzilla rules list
    Name           Source    Type    Status    Errors
    -------------  --------  ------  --------  --------
    err            user      lua     enabled   -

In unusual circumstances, the rule can be re-enabled without changing
it, using `logzilla rules enable` - this will also reset the error
counter and clean the error log for the given rule (the old error
messages would still be available via `logzilla logs`).

Finally, the error limit can be configured by the
`logzilla config RULE_ERROR_LIMIT` command, which sets the rate (per
hour) of failures that result in disabling of the rule (as mentioned,
this value is 5 by default).
