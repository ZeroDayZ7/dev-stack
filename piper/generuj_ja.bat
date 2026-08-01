@echo off
chcp 65001 > nul

set TARGET_DIR=C:\Users\Neo\Desktop\WWW\csof\csof_backend_v2\platform\services\ai-piper-tts\test\ja

:: Tworzenie podfolderu, jeśli nie istnieje
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo Generowanie japońskich plików audio...

:: 1. ERP Test (Japonia)
curl -X POST "http://localhost:8000/api/tts" ^
  -H "Content-Type: application/json; charset=utf-8" ^
  -d "{\"text\": \"ERPシステムは正常に動作しています。すべてのモジュールがアクティブです。\", \"speed\": 0.85, \"sentence_silence\": 0.75}" ^
  --output "%TARGET_DIR%\erp_test.wav"

:: 2. Raport operacyjny noc (Japonia)
curl -X POST "http://localhost:8000/api/tts" ^
  -H "Content-Type: application/json; charset=utf-8" ^
  -d "{\"text\": \"おはようございます。夜間サイクルの運用サマリーを開始します。すべての基幹システムが正常に検証されました。重大な障害やデータの損失は検出されていません。詳細レポートに移ります。第1項目。サーバーインフラストラクチャ。計算クラスタの自動メンテナンスが完了しました。サービスの可用性に影響を与えることなく、本番環境の更新を実行しました。メインデータセンターとバックアップデータセンター間の完全なバックアップ同期が完了しました。データリストアテストは成功しました。第2項目。ロジスティクスと倉庫。高回転商品の夜間配置最適化を実施しました。自動ピッキングシステムにより、注文準備の平均時間が短縮されました。取引先からのすべての配送について、書類および在庫との一致を確認しました。オペレーターの介入を必要とする不一致は検出されませんでした。第3項目。販売およびカスタマーサービス。販売プラットフォームは、レポート期間全体を通じて完全なサービス可用性を維持しました。自動分析メカニズムにより、TechSolutions Polska、Baltic Logistics、およびNova Industriesの製品に対する関心の高まりが検出されました。システムは今後24時間の需要増加予測を生成し、計画部門に推奨事項を送信しました。第4項目。顧客関係。チケット管理モジュールがすべての新しいメッセージを分析しました。人工知能が優先順位を割り当て、定型的な問い合わせに対する回答を自動的に作成しました。Orion Manufacturingとの協力に関する、即時分析が必要な案件が1件特定されました。担当チームに自動的に通知されました。第5項目。財務および会計。売上、コスト、在庫書類の夜間検証が完了しました。すべての取引が正しく記帳されました。多段階承認手順に従って、承認待ちの請求書が数件検出されました。税務上の不一致や会計上のエラーは記録されていません。第6項目。生産。技術ラインは計画された生産性を達成しました。品質モニタリングシステムは、生産パラメータが技術要件に適合していることを確認しました。許容品質公差の超過は検出されませんでした。第7項目。デジタルセキュリティ。夜間、海外アドレスからのログイン試行回数の増加が記録されました。保護メカニズムにより、すべての疑わしいセッションが自動的にブロックされました。セキュリティ違反や情報漏洩は確認されていません。すべてのイベントは監査ログに記録されました。第8項目。人事管理。システムは勤務スケジュールの同期を完了しました。出勤記録の完全性と、現在のシフトのチームの空き状況が検証されました。部門管理者向けの出勤レポートが自動的に生成されました。第9項目。ビジネス分析。予測モジュールは、売上、運用コスト、在庫需要の新しい予測を作成しました。モデルの精度は高い水準を維持しています。推奨されるアクションは管理パネルに送信されました。第10項目。システム状態。すべてのサービスが安定して動作しています。インフラストラクチャの負荷は閾値未満に収まっています。プラットフォームの稼働率は100％です。すべての夜間プロセスが正常に完了しました。運用レポートは以上です。穏やかで生産的な一日をお過ごしください。\", \"speed\": 0.80, \"sentence_silence\": 0.75}" ^
  --output "%TARGET_DIR%\raport_operacyjny_noc.wav"

:: 3. Raport prezesa (Japonia)
curl -X POST "http://localhost:8000/api/tts" ^
  -H "Content-Type: application/json; charset=utf-8" ^
  -d "{\"text\": \"社長、お疲れ様です。主要業績評価指標および運用サマリーを準備いたしました。今四半期のすべての目標は予定通りに進行しております。\", \"speed\": 0.85, \"sentence_silence\": 0.75}" ^
  --output "%TARGET_DIR%\raport_prezesa.wav"

echo.
echo [Sukces] Japońskie pliki audio zostały zapisane w %TARGET_DIR%
pause