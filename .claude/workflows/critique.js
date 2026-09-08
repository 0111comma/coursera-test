export const meta = {
  name: 'critique',
  description: '焼く前の批評パネル: 直近の指摘がクリアされたか・もっと良くするには・事実は正しいか を5人が審査し、指摘を docs/research/shiteki-stock.md に貯める',
  whenToUse: '台本を直したあと、焼く前に必ず。args: {video:"videos/<ID>-<slug>", feedback:"直近のユーザー指摘(原文)", date:"YYYY-MM-DD"}',
  phases: [
    { title: 'Critique', detail: '5人の審査員が独立に指摘を出す' },
    { title: 'Merge', detail: '重複を畳み、既存ゲートで止まるものを除き、重さを付ける' },
    { title: 'Stock', detail: 'shiteki-stock.md に追記する' },
  ],
}

const video = args?.video || 'videos/Z001-joushi-kigen'
const feedback = args?.feedback || '(直近の指摘なし)'
const date = args?.date || '(日付は args.date で渡す)'

const FINDINGS = {
  type: 'object', required: ['critic', 'findings', 'summary'],
  properties: {
    critic: { type: 'string' },
    summary: { type: 'string', description: '3行以内。何を見て、いちばん重い問題は何か' },
    findings: { type: 'array', items: { type: 'object',
      required: ['title', 'severity', 'where', 'why', 'fix'],
      properties: {
        title: { type: 'string', description: '指摘を1行で(名詞止めにしない。「〜が無い」「〜と読める」)' },
        severity: { type: 'string', enum: ['high', 'medium', 'low'], description: 'high=この指摘が残ったまま出すと視聴者に嘘か無学びになる / medium=直せば明らかに良くなる / low=好み' },
        where: { type: 'string', description: 'カット番号か plan.md の節。全体なら「全体」' },
        why: { type: 'string', description: '根拠。台本の原文を引用する' },
        fix: { type: 'string', description: '直し。ナレーションなら**置き換え後の文そのもの**を書く。方針だけの直しは無効' },
      } } },
  },
}

const COMMON = `対象の動画: ${video}
読むもの(この順で、全部読むこと):
1. ${video}/render.py の UNITS(ナレーション=字幕。これが視聴者に届く全文)と SCENES(画面)
2. ${video}/plan.md(企画書。§1 欲求、§1.5 知らなかった、§1.7 学び、§9 結論、§10 前提と根拠)
3. docs/research/shiteki-stock.md があれば、既に出ている指摘(同じ指摘は出さない。**新しい種類の指摘だけ**出す)
4. production/check_*.py の先頭の docstring だけ(機械ゲートで既に止まる指摘は出さない)

チャンネル: 「ヤケに心理学に詳しいずんだもん」。哲学・心理学の**知識を分け与える**ショート(縦型・3分以内)。
主な視聴者: 35歳の男性会社員(P-M)。前情報ゼロで、字幕を1回だけ順に読む。

直近のユーザー指摘(原文):
「${feedback}」

出力は StructuredOutput で。fix は方針ではなく**置き換え後の文**。severity は基準どおりに付ける(全部 high にしない)。`

const CRITICS = [
  { key: 'clear', prompt: `${COMMON}

あなたの役: **指摘クリア判定人**。直近のユーザー指摘を、問いごとに分解し(例: 「誰が言ったの?」「なぜこの本が残ってるの?」「誰になぜ評価されているの?」「学びがあるか」)、
**台本の字幕だけを読んだ視聴者が、その問いに答えられるか**を1問ずつ判定する。
答えられない・曖昧・「なぜ」が抜けている(例: 皇帝が読んだ、はあるが**なぜ**皇帝が価値を認めたかが無い)ものを finding にする。
クリアできている問いも summary に書く(何カットのどの文で答えているか)。` },
  { key: 'manabi', prompt: `${COMMON}

あなたの役: **学びの深さの審査員**(大学で哲学史を教えている人として)。
この動画を見た35歳会社員が「知らなかった」と言える知識は何か、全部列挙する。
そのうえで、**同じ尺で足せる、もっと価値の高い知識**(例: 皇帝がなぜ元奴隷の本を大事にしたか / 修道院が何を読み取ったか / 認知行動療法が具体的にどう使うか / 『提要』の1章と5章の関係)を、
**ナレーション1〜2文の形で**提案する。薄い・雑学止まり・一般論になっているカットも指摘する。` },
  { key: 'fact', prompt: `${COMMON}

あなたの役: **事実の検証人**(古典学の校閲者として)。
ナレーションの歴史的・学術的な主張を1文ずつ抜き出し、plan.md §1.7・§10 の出典と照らして、
(a) 出典で裏付く (b) 出典が無い/弱い (c) 言い過ぎ・不正確(例: 「病院にある」「1000年」「生まれつき奴隷」「日記」「ありがとうって書いてる」の言い方は原典と合うか)
を判定する。(b)(c) を finding にし、**正確で、かつ話し言葉のまま**の置き換え文を書く。あなた自身の知識で明らかに違うものは severity high。` },
  { key: 'retention', prompt: `${COMMON}

あなたの役: **維持率の審査員**(ショート動画の編集者として)。
字幕を順に読み、**どのカットでスワイプするか**を秒単位で言う(1カット約2.5秒)。
学びの幕(11〜28カット)が長くてだれていないか、山(se=don)が効いているか、1コマ目からの期待と後半が繋がっているか、
締めが行動(メモに1行)に戻れているか。だれるカットは「畳む/切る/順番を変える」の具体案(置き換え後の文)を書く。` },
  { key: 'persona', prompt: `${COMMON}

あなたの役: **視聴者そのもの**(35歳・男性・会社員。今日上司に一言言われて帰りの電車にいる。哲学も心理学も知らない)。
字幕を1回だけ順に読んだあと、(1) 何を覚えているか (2) 明日誰かに話すとしたら何と言うか (3) 「で、結局何なの?」と思った箇所 (4) 信じられない・胡散臭いと感じた箇所 (5) もっと知りたくなった箇所
を、あなたの言葉で書く。(3)(4) を finding にし、(5) は fix に「足すならこの1文」を書く。` },
]

const MERGED = {
  type: 'object', required: ['items', 'high', 'summary'],
  properties: {
    summary: { type: 'string' },
    high: { type: 'number', description: 'high の件数' },
    items: { type: 'array', items: { type: 'object',
      required: ['title', 'severity', 'where', 'why', 'fix', 'critics', 'status'],
      properties: {
        title: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
        where: { type: 'string' }, why: { type: 'string' }, fix: { type: 'string' },
        critics: { type: 'string', description: 'この指摘を出した審査員(clear/manabi/fact/retention/persona をカンマ区切り)' },
        status: { type: 'string', enum: ['未対応', 'ゲート化済み(既存ゲートで止まる)', '既出(stock に同じ指摘がある)'] },
      } } },
  },
}

phase('Critique')
log(`批評パネル ${CRITICS.length} 人を ${video} に回す`)
const raw = await parallel(CRITICS.map(c => () =>
  agent(c.prompt, { label: `critic:${c.key}`, phase: 'Critique', schema: FINDINGS })
    .then(r => r && { ...r, critic: c.key })))
const results = raw.filter(Boolean)
const all = results.flatMap(r => r.findings.map(f => ({ ...f, critic: r.critic })))
log(`指摘 ${all.length} 件(high ${all.filter(f => f.severity === 'high').length})`)

phase('Merge')
const merged = await agent(`次の指摘(JSON)を整理する。
1. 同じ内容は1つに畳む(critics に出した審査員を全部残す。severity は最も重いものを採る)
2. production/check_*.py の docstring を読み、**既存の機械ゲートで止まる指摘**は status を「ゲート化済み(既存ゲートで止まる)」にする
3. docs/research/shiteki-stock.md があれば読み、同じ指摘は「既出(stock に同じ指摘がある)」にする
4. 残りは「未対応」。fix が方針だけのものは、台本(${video}/render.py の UNITS)を読んで**置き換え後の文**に書き直す
5. severity の基準: high=残したまま出すと嘘か無学び / medium=直せば明らかに良くなる / low=好み
6. summary に、審査員5人の summary を1行ずつ引用する

指摘:
${JSON.stringify(all, null, 1)}`, { label: 'merge', phase: 'Merge', schema: MERGED })

phase('Stock')
const stock = await agent(`docs/research/shiteki-stock.md に、次の指摘を**追記**する(無ければ作る。既存の行は消さない)。

ファイルの形式(無ければこの見出しと表頭を作る):
# 指摘ストック(批評パネル .claude/workflows/critique.js が貯める)

状態: 未対応 / 対応済み(コミット) / ゲート化済み(check_*.py) / 見送り(理由)。
**焼く前に high が 0 であること。** 対応したら状態を書き換え、2本以上の動画で出た指摘は CLAUDE.md かゲートへ。

| ID | 日付 | 動画 | 審査員 | 重さ | 指摘 | 根拠 | 直し | 状態 |
|---|---|---|---|---|---|---|---|---|

- ID は「動画ID-連番」(例 Z001-01)。既存の行の最大連番の次から振る
- 日付 ${date}、動画 ${video.split('/').pop()}
- 表のセル内の改行は消し、| は／に置き換える
- 追記したあと、追記した行数と、high の件数を返す

指摘:
${JSON.stringify(merged.items, null, 1)}`, { label: 'stock', phase: 'Stock' })

return { high: merged.high, items: merged.items, summary: merged.summary, stock }
