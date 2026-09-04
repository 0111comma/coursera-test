export const meta = {
  name: 'coldread',
  description: '前情報ゼロの読者4人が字幕だけを順に読み、(a)何の話か (b)自分なら絶対に言わない文 を全カットで挙げ、直す',
  phases: [
    { title: '冷読', detail: '4人が字幕だけを順に読む。全カットに「言わない文」判定を付ける' },
    { title: '採点', detail: '場面の復元と、2人以上が「言わない」とした文を集計' },
    { title: '書き直し', detail: '言わない文を人が言う形に。前のカットだけで分かる形に' },
  ],
}
// 使い方: Workflow({ name: 'coldread', args: { video: 'videos/Z001-joushi-kigen', rounds: 2 } })
// **plan.md は読者に渡さない。**面白さ・日本語の審査より先に、必ずこれを回す(CLAUDE.md)。
const REPO = '/home/user/coursera-test'
const VIDEO = args.video
const MAX_ROUNDS = args.rounds || 2

const READ_SCHEMA = {
  type: 'object', required: ['perCut', 'retell', 'lostAt', 'understood'],
  properties: {
    perCut: { type: 'array', items: { type: 'object', required: ['cut', 'guess', 'wouldSay', 'natural'], properties: {
      cut: { type: 'number' },
      guess: { type: 'string', description: 'このカットまで読んで、いま何の話だと思うか(1文。分からなければ「分からない」)' },
      wouldSay: { type: 'boolean', description: 'この文を、自分が友だちに喋るときにそのまま口にするか' },
      natural: { type: 'string', description: 'wouldSay が false のとき、自分ならこう言う(30字以内)。true なら空' },
    } } },
    retell: { type: 'string', description: '全部読んだあと「誰が・何をされて・どこで・どうする話か」を自分の言葉で' },
    lostAt: { type: 'number', description: '最初に「何の話?」となったカット(0=無し)' },
    understood: { type: 'number', description: '0-10' },
  },
}
const GRADE_SCHEMA = {
  type: 'object', required: ['pass', 'score', 'brokenCuts', 'neverSay', 'summary'],
  properties: {
    pass: { type: 'boolean', description: '全員が場面と結論を復元し、lostAt が全員0で、3人以上(4人中の過半数)が「言わない」とした文が0のときだけ true' },
    score: { type: 'number' }, summary: { type: 'string' },
    brokenCuts: { type: 'array', items: { type: 'object', required: ['cut', 'why', 'rewrite'], properties: { cut: { type: 'number' }, why: { type: 'string' }, rewrite: { type: 'string' } } } },
    neverSay: { type: 'array', items: { type: 'object', required: ['cut', 'line', 'votes', 'rewrite'], properties: {
      cut: { type: 'number' }, line: { type: 'string' }, votes: { type: 'number', description: '「言わない」とした人数' },
      rewrite: { type: 'string', description: '読者の natural から、いちばん自然で前後とつながるもの(30字以内)' } } } },
  },
}
const READERS = [
  '35歳の会社員。心理学も哲学も知らない。YouTubeショートは寝る前に流し見する',
  '28歳の営業職。ずんだもんの動画は見たことがある。本は読まない',
  '42歳の事務職。難しい言葉が出た瞬間にスワイプする。今日は疲れている',
  '24歳の新入社員。上司との関係で悩んだことはまだ無い。スマホの字幕を音無しで読む',
]
function readerPrompt(who) {
  return `あなたは${who}。
YouTube ショートの字幕を、**上から順に1回だけ**読む。**戻って読み直さない。企画書・図・タイトル・概要欄は渡さない。字幕だけ。**
取り出し方(これ以外のファイルは読むな): cd ${REPO} && python3 -c "import sys,importlib.util;sys.path.insert(0,'production');s=importlib.util.spec_from_file_location('r','${VIDEO}/render.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);[print(i+1,u.subtitle) for i,u in enumerate(m.UNITS)]"

**全カットについて**、次の2つを答える:
(a) このカットまで読んで、いま何の話だと思うか(guess)。分からなければ「分からない」
(b) **この文を、自分が友だちに喋るときにそのまま口にするか**(wouldSay)。
    しないなら、**自分ならこう言う**(natural)。理由は要らない。言い換えた文だけ書く。
    「意味は分かるけど、こうは言わない」も **false** にする(例: 「言い方を直す」→ 人は「ああ言えばよかった」と言う)
最後に: 最初に「何の話?」となったカット(lostAt)/ 誰が・何をされて・どこで・どうする話かの言い直し(retell)/ 理解度 0-10(understood)。
**専門家として直そうとするな。自分の口から出る言い方だけを書け。**`
}

let finalGrade = null
for (let round = 1; round <= MAX_ROUNDS; round++) {
  phase('冷読')
  const reads = await parallel(READERS.map((who, i) => () =>
    agent(readerPrompt(who), { label: `冷読R${round}:読者${i + 1}`, phase: '冷読', schema: READ_SCHEMA }).then(r => ({ who, r })).catch(() => null)))
  const ok = reads.filter(x => x && x.r)
  if (!ok.length) { log('読者が全滅'); break }
  log(`R${round} 理解度 ${ok.map(x => `${x.r.understood}(lost@${x.r.lostAt})`).join(' ')} / 言わない文の票 ${ok.map(x => (x.r.perCut || []).filter(c => c.wouldSay === false).length).join('+')}`)

  phase('採点')
  const grade = await agent(`あなたは採点者。前情報ゼロの読者4人の結果を集計しろ。
企画書(場面と結論の正解): ${REPO}/${VIDEO}/plan.md の §2・§4・§9。字幕: ${REPO}/${VIDEO}/render.py の UNITS
読者4人の結果:
${ok.map((x, i) => `--- 読者${i + 1}(${x.who})\n理解度 ${x.r.understood} / lostAt #${x.r.lostAt}\n言い直し: ${x.r.retell}\n${(x.r.perCut || []).map(c => `  #${c.cut} [${c.wouldSay ? '言う' : '言わない'}] ${c.guess}${c.wouldSay ? '' : ` → 自分なら「${c.natural}」`}`).join('\n')}`).join('\n')}

やること:
1. 場面の復元: 1コマ目で「誰に何をされてどこで」が全員に復元できているか。各カットは前のカットだけで分かるか(brokenCuts)
2. **「言わない」の集計**: カットごとに「言わない」とした人数(votes)を数え、**3人以上**(4人中の過半数)の文を neverSay に全部並べる。2人は好みの差なので載せない。
   rewrite は読者の natural の中から、いちばん自然で前後とつながるものを選ぶ(必要なら少し整える。30字以内)
3. pass は、全員 lostAt=0・retell が §9 と一致・neverSay が 0 件のときだけ true`,
    { label: `採点R${round}`, phase: '採点', schema: GRADE_SCHEMA }).catch(() => null)
  if (!grade) break
  finalGrade = grade
  log(`R${round} 採点 ${grade.score} pass=${grade.pass} 落ちたカット=${(grade.brokenCuts || []).map(b => b.cut).join(',')} 言わない文=${(grade.neverSay || []).map(n => `#${n.cut}(${n.votes})`).join(',')}`)
  if (grade.pass || round === MAX_ROUNDS) break

  phase('書き直し')
  await agent(`あなたはこのチャンネルの脚本担当。**読者が「自分なら絶対に言わない」とした文を、読者の言い方に直せ。**
ユーザーの指示: 「そのチェック全てで行え」——分かるかどうかだけでなく、**全カットを人が口にする形にする**。
対象: ${REPO}/${VIDEO}/render.py の UNITS(図の文言 SCENES も合わせる)。
言わない文(2人以上):
${(grade.neverSay || []).map(n => `#${n.cut} 「${n.line}」(${n.votes}人) → 「${n.rewrite}」`).join('\n')}
分からなかったカット:
${(grade.brokenCuts || []).map(b => `#${b.cut}: ${b.why} → 「${b.rewrite}」`).join('\n')}
守ること: プロットの骨は保つが、分かりやすさと自然さが優先 / 1カット30字以内 / 新しい数字を出さない / 二人称と問いは4カットに1回以上 /
接続は話し言葉の受け(で、/てか/じゃあ/だって)か名詞の繰り返し。「では・まず・一方・つまり」は使わない。
手順: 1) UNITS を直す 2) cd ${REPO} && python3 production/check_flow.py ${VIDEO} と check_honyaku / check_bunsho / check_kotoba / check_tempo / check_toi / check_goi / check_teinei / check_figure を回して落ちたものを直す(**ゲートを通すために書き言葉に戻すのは禁止**。ゲートが話し言葉を落としたら notes に書け) 3) ${VIDEO}/script.md のナレーション表を更新 4) plan.md §4 の1コマ目を同期`,
    { label: `書き直しR${round}`, phase: '書き直し' }).catch(() => null)
}
return { grade: finalGrade }
