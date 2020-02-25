#!/bin/bash

set -e

prompt()
{
  local message=$1
  echo "========================================"
  echo "$message"
  echo -n "Please enter: "
  read -r
}

run()
{
  echo "$ python main.py $*"
  python main.py "$@"
  echo
}

rm -f datafile.pickle

prompt "ユーザを作成する"
run user create --name "Customer 1" --role "customer"
run user create --name "Customer 2" --role "customer"
run user create --name "Test Support"  --role "support"

prompt "ユーザ一覧を確認"
run user list

prompt "顧客1, 2 それぞれから要望を作成する"
run feedback create \
    --title="顧客1からの機能追加の要望" \
    --description="あれこれと便利な機能を追加してほしいです" \
    --user_id=1

run feedback create \
    --title "顧客2からの機能追加の要望" \
    --description "あれこれと便利な機能を追加してほしいです" \
    --user_id 2

prompt "サポートユーザは、全ての要望を確認できる"
run feedback list --user_id 3

prompt "顧客は、自分の作成した要望だけを確認できる"
run feedback list --user_id 1
