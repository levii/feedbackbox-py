#!/bin/bash

prompt()
{
  local message=$1
  echo "========================================"
  echo "$message"
  echo -n "Please enter: "
  read -r
}

rm -f datafile.pickle

prompt "ユーザを作成する"
python main.py user create --name "Customer 1" --role "customer"
python main.py user create --name "Customer 2" --role "customer"
python main.py user create --name "Test Support"  --role "support"
echo

prompt "ユーザ一覧を確認"
python main.py user list
echo

prompt "顧客1, 2 それぞれから要望を作成する"
python main.py feedback create \
    --title="顧客1からの機能追加の要望" \
    --description="あれこれと便利な機能を追加してほしいです" \
    --user_id=1

python main.py feedback create \
    --title "顧客2からの機能追加の要望" \
    --description "あれこれと便利な機能を追加してほしいです" \
    --user_id 2
echo

prompt "サポートユーザは、全ての要望を確認できる"
python main.py feedback list --user_id 3
echo

prompt "顧客は、自分の作成した要望だけを確認できる"
python main.py feedback list --user_id 1
echo
