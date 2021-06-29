Here are some vscode JSON launch configs for the latest mid-2021 tests

```json
        {
            "name": "test PYTHON parsing edge cases - test_issue_typehint_optional",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceRoot}/src",
            "module": "unittest",
            "args": [
                "tests.test_parse_bugs_incoming.TestIncomingBugs.test_issue_typehint_optional",
            ],
        }, 
        {
            "name": "test_issue_subscript_issue_93",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceRoot}/src",
            "module": "unittest",
            "args": [
                "tests.test_parse_bugs_incoming.TestIncomingBugs.test_issue_subscript_issue_93",
            ],
        }, 
        {
            "name": "test_issue_walrus_issue_94",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceRoot}/src",
            "module": "unittest",
            "args": [
                "tests.test_parse_bugs_incoming.TestIncomingBugs.test_issue_walrus_issue_94",
            ],
        }, 
        {
            "name": "test_issue_class_type_annotation_85",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceRoot}/src",
            "module": "unittest",
            "args": [
                "tests.test_parse_bugs_incoming.TestIncomingBugs.test_issue_class_type_annotation_85",
            ],
        }, 
```
