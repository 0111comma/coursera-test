export const meta = {
  name: 'nihongo',
  description: '日本語の審査パネル: 定訳・翻訳調・耳・話し言葉・校閲の5人が100点満点で採点し、合格点を下回ったら不合格。指摘は docs/research/nihongo-stock.md に貯める',
  whenToUse: '台本を直したあと、焼く前に。args: {video:"videos/<ID>-<slug>", date:"YYYY-MM-DD", pass:80}',
  phases: [
    { title: 'Review', detail: '5人が独立に採点し、直す文を書く' },
    { title: 'Merge', detail: '重複を畳み、合計点と合否を出す' },
    { title: 'Stock', detail: 'nihongo-stock.md に追記する' },
  ],
}

const video = args?.video || 'videos/Z001-joushi-kigen'
const date = args?.date || '(日付は args.date で渡す)'
const PASS = args?.pass ?? 80

const SCORED = {
  type: 'object', required: ['critic', 'score', 'findings', 'summary'],
  properties: {
    critic: { type: 'string' },
    score: { type: 'number', description: '0〜100。**この観点だけ**の点。90=商業品質 / 80=公開してよい / 70=直しが要る / 60以下=作り直し' },
    summary: { type: 'string', description: '3行以内。何点で、なぜその点か' },
    findings: { type: 'array', items: { type: 'object',
      required: ['cut', 'line', 'kind', 'why', 'fix'],
      properties: {
        cut: { type: 'number', description: 'カット番号。全体なら 0' },
        line: { type: 'string', description: '直す前の文(原文のまま)' },
        kind: { type: 'string', description: '型を短く。例: 直訳の対比 / 定訳の欠落 / 接続語の連発 / 語尾の単調 / 助詞の誤り / 主語の欠落' },
        why: { type: 'string', description: 'なぜ日本語としてまずいか。「英語ならこう」も書いてよい' },
        fix: { type: 'string', description: '**置き換え後の文そのもの**。方針だけは無効' },
      } } },
  },
}

const COMMON = `対象: ${video}
読むもの:
1. ${video}/render.py の UNITS(ナレーション=字幕。これが読み上げられる全文)
2. ${video}/plan.md の §1.7 学び・§10 前提と根拠(専門語の出典)
3. production/teiyaku.txt(専門語の定訳の一覧)
4. docs/research/nihongo-stock.md があれば既出の指摘(同じ指摘は出さない)
5. docs/research/ai-nihongo-rules.md(翻訳調 T1〜T10)

チャンネル: 「ヤケに心理学に詳しいずんだもん」。哲学・心理学の知識を渡す縦型ショート(3分以内)。
語り手はずんだもん(タメ口。ただし幼くしすぎない)。聞き手は35歳の男性会社員。
**耳で1回だけ聞く**。字幕は同じ文が出る。

直近のユーザー指摘(2026-09-05・原文):
「もうちょっと日本語ちゃんとしたい。英語を直訳したものに見えるのでしっかり専門用語は日本語で使われている表現をしましょう。」

採点は辛く。fix は必ず**置き換え後の文**を書く。`

const CRITICS = [
  { key: 'teiyaku', prompt: `${COMMON}

あなたの役: **専門語の定訳の審査員**(哲学・心理学の訳書の編集者として)。
ナレーションに出てくる哲学・心理学の概念を全部挙げ、それぞれについて
(a) 日本語で定着している呼び方(定訳)は何か
(b) 動画はその定訳を1回でも言っているか
(c) 言い換えだけで済ませていないか
を判定する。定訳を言っていないものを finding にし、**定訳を出したうえで普通の言葉に置き換える1〜2文**を書く。
例: 「エピクテトスはこれを「権内にあるもの」って呼んだの。要は、自分の力が届くもの。」
定訳が難しすぎて視聴者が固まる場合も、**言わない**のではなく**言ってすぐ崩す**形にする。
逆に、定訳を使っているのに意味を取り違えているもの(例: 論理療法と認知行動療法を同じものとして扱う)も挙げる。` },
  { key: 'chokuyaku', prompt: `${COMMON}

あなたの役: **翻訳調ハンター**。1文ずつ、英語に直訳して戻る文を挙げる。
特に見るもの: (a)「AじゃなくB」= not A but B の直訳 (b) 無生物主語 (c) 「〜することができる」
(a2) **文頭の逆接(でも/しかし/けど/ところが)を全部拾い、「前の文の何を打ち消しているか」を
     1語で言えるかを確かめる。言えないものは全部 finding にする**
     (2026-09-07 ユーザー「ここの接続詞『でも』おかしくない? 絶対そのまま翻訳してるよね? 直訳。ダメだよ。」)。
     check_flow は「その文の中に否定語があるか」しか見ておらず、日本語の文はたいてい
     否定語を含むので素通りする。**逆接が成り立っているかは前の文を読まないと決まらない**ので、
     ここが最後の網になる。話題を変えているだけなら「さて」「ちなみに」に替える
(d) 関係節の直訳(「〜した人が言った言葉が…」) (e) 対比・列挙を英語の語順のまま置いた文
(f) 引用が英訳からの重訳になっていないか(古典の引用は日本語の定訳に寄せる)。
finding には「英語ならこうなる」を why に書き、fix に**日本語として自然な文**を書く。` },
  { key: 'mimi', prompt: `${COMMON}

あなたの役: **耳で聞く人**。字幕を見ずに、声だけで1回聞くつもりで全カットを読む。
(a) 同じ音が続いて聞き取れない (b) 助詞が抜けて意味が2通りになる (c) 1文が長くて息が続かない
(d) 同音異義語(こうてい=皇帝/肯定、しんり=心理/真理)が文脈なしに出る
(e) 「〜って」「〜の」が続いて誰の発言か分からない
を挙げ、fix に**声で通る文**を書く。` },
  { key: 'hanashi', prompt: `${COMMON}

あなたの役: **話し言葉の審査員**。ずんだもんが実際に言う文になっているかを見る。
(a) 文頭の接続語(「で、」「だから」「しかも」)の連発 — 何カットが同じ語で始まるか数える
(b) 語尾の単調(「〜なの。」「〜って。」「〜んだって。」の連続)
(c) 幼すぎて内容が軽くなっている箇所、逆に硬すぎて浮いている箇所
(d) 質問(「〜でしょ?」「知ってた?」)の乱発
を挙げ、fix に**接続語を貼らずに繋がる文**を書く(前の文の名詞をもう一度言う・文を続ける・語順を変える)。` },
  { key: 'kouetsu', prompt: `${COMMON}

あなたの役: **校閲**(出版社の校閲部として)。
(a) 誤用・ら抜き・重複表現 (b) 係り受けの乱れ (c) 指示語が何を指すか一意でない
(d) 数え方・単位・固有名の表記ゆれ(『提要』/『要録』、皇帝の名、書名の記号)
(e) 事実と語のズレ(「〜が言った」「〜が書いた」の主語が出典と違う)
を挙げ、fix に**直した文**を書く。表記ゆれは動画全体で1つに統一する案を出す。` },
]

const MERGED = {
  type: 'object', required: ['total', 'pass', 'items', 'summary'],
  properties: {
    total: { type: 'number', description: '5人の点の平均(小数1桁)' },
    pass: { type: 'boolean', description: `平均が ${PASS} 以上で、かつ「定訳の欠落」が0件なら true` },
    summary: { type: 'string' },
    items: { type: 'array', items: { type: 'object',
      required: ['cut', 'line', 'kind', 'critics', 'fix', 'severity'],
      properties: {
        cut: { type: 'number' }, line: { type: 'string' }, kind: { type: 'string' },
        critics: { type: 'string' }, fix: { type: 'string' },
        severity: { type: 'string', enum: ['high', 'medium', 'low'],
                    description: 'high=定訳の欠落か、日本語として明らかに誤り / medium=直訳調・接続語の連発 / low=好み' },
      } } },
  },
}

phase('Review')
log(`日本語パネル ${CRITICS.length} 人を ${video} に回す(合格点 ${PASS})`)
const raw = await parallel(CRITICS.map(c => () =>
  agent(c.prompt, { label: `nihongo:${c.key}`, phase: 'Review', schema: SCORED })
    .then(r => r && { ...r, critic: c.key })))
const results = raw.filter(Boolean)
const all = results.flatMap(r => r.findings.map(f => ({ ...f, critic: r.critic })))
log(`採点: ${results.map(r => `${r.critic} ${r.score}`).join(' / ')} — 指摘 ${all.length} 件`)

phase('Merge')
const merged = await agent(`5人の日本語審査員の採点と指摘(JSON)を整理する。

採点: ${JSON.stringify(results.map(r => ({ critic: r.critic, score: r.score, summary: r.summary })), null, 1)}

指摘:
${JSON.stringify(all, null, 1)}

やること:
1. 同じ文への指摘は1つに畳む(critics に出した審査員を全部残す。severity は最も重いものを採る)
2. fix が矛盾する場合は、**${video}/render.py の前後のカットを読んで**どちらが通るか決め、1つの文にする
3. total = 5人の点の平均。pass = total が ${PASS} 以上 かつ severity high(定訳の欠落・明らかな誤り)が0件
4. production/check_teiyaku.py・check_honyaku.py・check_flow.py・check_bunsho.py の docstring を読み、
   **既存の機械ゲートで止まる指摘**は kind の先頭に「(ゲート済)」を付ける
5. summary に、5人の summary を1行ずつ引用し、最後に「いちばん重い1件」を書く`,
  { label: 'merge', phase: 'Merge', schema: MERGED })

phase('Stock')
const stock = await agent(`docs/research/nihongo-stock.md に次の指摘を**追記**する(無ければ作る。既存の行は消さない)。

ファイルの形式(無ければこの見出しと表頭を作る):
# 日本語の指摘ストック(.claude/workflows/nihongo.js が貯める)

2026-09-05 ユーザー「もうちょっと日本語ちゃんとしたい。英語を直訳したものに見えるので
しっかり専門用語は日本語で使われている表現をしましょう。」

**合格点は平均 ${PASS} 点。定訳の欠落(high)が1件でもあれば、点に関係なく不合格。**
状態: 未対応 / 対応済み(コミット) / ゲート化済み(check_teiyaku.py 等) / 見送り(理由)。

## 採点の記録

| 日付 | 動画 | 定訳 | 翻訳調 | 耳 | 話し言葉 | 校閲 | 平均 | 合否 |
|---|---|---|---|---|---|---|---|---|

## 指摘

| ID | 日付 | 動画 | カット | 型 | 審査員 | 重さ | 直す前 | 直し | 状態 |
|---|---|---|---|---|---|---|---|---|---|

- 採点の記録に1行足す: 日付 ${date}、動画 ${video.split('/').pop()}、各人の点、平均 ${merged.total}、合否 ${merged.pass ? '合格' : '不合格'}
- 指摘は ID「動画ID-N番」(例 Z001-J01)。既存の最大番号の次から振る
- 表のセル内の改行は消し、| は／に置き換える。長い文は要点だけ
- 追記した行数を返す

各人の点: ${JSON.stringify(results.map(r => ({ critic: r.critic, score: r.score })))}
指摘:
${JSON.stringify(merged.items, null, 1)}`, { label: 'stock', phase: 'Stock' })

return { total: merged.total, pass: merged.pass, scores: results.map(r => ({ critic: r.critic, score: r.score })),
         high: merged.items.filter(i => i.severity === 'high').length, items: merged.items,
         summary: merged.summary, stock }
