# AkariLauncher Pacman

このリポジトリはAkariLauncherで使用できる独自のリポジトリーを作成するための物です。

## 使い方

1. プロジェクトをinitする

```
python main.py --init

> リポジトリ名を入力してください
> リポジトリに使用するサービスを指定してください。github, gitlab, s3
> base_urlを指定してください。 githubなどはrawのブランチまでを指定してください
```

2. modpackを作成する

|引数名|説明|
|---|---|
|--name|ModPackの名前|
|--version|ModPackのバージョン|
|--mc-version|Minecraftのバージョン|
|-n|ModPackを新規に作成することを明示するフラグ|

```
python ./main.py --name testpack --version 1.0.0 --mc-version 1.7.10 -n
```

3. 編集モードに入る

|引数名|説明|
|---|---|
|-e|editモードに入ることを明示するフラグ|

```
python ./main.py --name testpack --version 1.0.0 --mc-version 1.7.10 -e
```

4. tmp_modpacks/modpack名でフォルダが作成されるので modsにはmodを resourcesには configフォルダやshadersなどを設置します。ほとんどのファイル・フォルダを使用できますが、空のフォルダは使用できません

5. 変更を適応する

|引数名|説明|
|---|---|
|--apply|変更を適応することを明示するフラグ|

```
python ./main.py --name testpack --version 1.0.0 --mc-version 1.7.10 -e --apply
```

## よくありそうな質問

### ModPackをリリースしたり、変更を適応するとModやconfigのデータが消えるのは何故ですか?

このプロジェクトでは同じModを複数配置しないことで容量の削減を行うため、Modをツールで管理しています。そのため、変更の適応やリリースを行うと`store/files`フォルダにファイルが移動されるため消えた様に見えます。


## 編集モードについて

編集モードは`store/files`から指定したmodpackの指定したバージョンのファイルを`tmp_modpack/modpack名`フォルダに元通りに復元し、modの追加や削除、ファイルの編集などが行える状態をさします。この状態を適応するには 編集モードに入った際のフラグに `--apply` を付けることで変更が保存されます。この際Modやファイルが削除された場合は全てのModPack、ModPackのバージョンにおいて他に使用されてない場合は `store/files` 上からも削除されます。

