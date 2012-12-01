PROJECT_WORKSPACE="$HOME/workspace-gae/newseditor"
export PYTHONPATH="$HOME/bin/google_appengine:$PYTHONPATH"
export PYTHONPATH="$PROJECT_WORKSPACE/src/library:$PYTHONPATH"
export PYTHONPATH="$PROJECT_WORKSPACE/src:$PYTHONPATH"
python "$PROJECT_WORKSPACE/test/unit/testpage/testpageanalyst.py"

