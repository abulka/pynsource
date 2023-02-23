# Fix permissions on the .app because it is not signed (which would cost me approx AUD $150 each year)
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
APP_NAME="Pynsource.app"
APP=$SCRIPTPATH/$APP_NAME
xattr -dr com.apple.quarantine $APP
# check if error
if [ $? -eq 0 ]; then
    echo "Success: $APP_NAME permissions fixed - you should be able to run it now"
    osascript -e 'display dialog "permissions fixed"'
else
    echo "Error fixing permissions"
    osascript -e 'display dialog "Error fixing permissions"'
fi
