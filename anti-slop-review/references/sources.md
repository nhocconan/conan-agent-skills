# AI slop: catalogue of signs and sources (researched 29/09/2026)

Scope: signs a staff member meets when AI drafts captions, emails, reports, slides. Grouped A Từ ngữ, B Mẫu câu, C Trình bày, D Nội dung. Each sign carries a source status:

- **WP** = quoted verbatim from Wikipedia "Signs of AI writing" (live page, fetched 29/09/2026; quotes re-checked with grep -F and independently re-verified). Page carries `{{update|the most recent models|type=page|date=August 2026}}`, so treat all its signs as "observed 2023-2026, model mix changing".
- **paper** = arXiv abstract or full text saved under `sources/` (only what was read is quoted).
- **BVN** = Brands Vietnam Help Desk "Dấu hiệu nhận biết nội dung được viết bởi AI" (page shows "Cập nhật vào: 23/09/2025"). A Vietnamese trade article, not research.
- **quan sát thực tế** = owner observation (29/09/2026) plus practitioner patterns. Not research. Every Vietnamese phrase list in this file has this status unless marked BVN.

Detectability: **script** = regex/heuristic catches it with few false positives; **script+human** = a script can flag candidates, a human decides; **human** = judgment only.

Baseline caveat (WP, Caveats): "Do not solely rely on [[artificial intelligence content detection]] tools ... these tools have non-trivial error rates." And: "Humans are notoriously bad at distinguishing human and LLM-generated text." A sign is a cue to edit, not proof of authorship.

Definition used in the lesson. Kommers et al., "Why Slop Matters" (arXiv 2601.06060, abstract): prototypical slop shows "superficial competence (its veneer of quality is belied by a deeper lack of substance), asymmetry effort ... and mass producibility". Shaib et al., "Measuring AI 'Slop' in Text" (arXiv 2509.19163v2, Appendix): seven codes, of which the two the lesson leans on are "Density – Many words, little information; filler or fluff." and "Structure – Repetitive or templated sentence / formula pattern." The same paper finds "binary 'slop' judgments are (somewhat) subjective".

---

## A · Từ ngữ (words)

### A1. Bộ ba tính từ / rule of three
- VI: "Đột phá. Tinh tế. Khác biệt." EN: "Bold. Refined. Different."
- Why AI: WP, Rule of three: "LLMs overuse the rule of three. This can take different forms, from 'adjective, adjective, adjective' to 'short phrase, short phrase, and short phrase'. LLMs often use this structure to make superficial analyses appear more comprehensive."
- Fix: replace the triplet with one fact. Before: "Đột phá. Tinh tế. Khác biệt." After: "Thân thép hai lớp, đá còn nguyên tới chiều."
- Source: WP. Detect: script+human (three consecutive one-word sentences, or "X, Y và Z" adjective lists; humans use triads too).

### A2. Từ khoa trương / AI vocabulary and puffery
- VI: "giải pháp toàn diện", "nâng tầm thương hiệu", "đóng vai trò then chốt", "hành trình", "bức tranh toàn cảnh" (quan sát thực tế; Finhay 2026 blog lists the same words, saved at `sources/finhay-chatgpt-van-mau.html`, not research). EN: "delve", "tapestry", "testament", "pivotal", "robust", "vibrant", "showcase", "underscore", "boasts".
- Why AI: WP, AI vocabulary: "Many studies have demonstrated that LLMs overuse specific words ... an edit (post-2022) introducing lots of them, lots of times, is one of the strongest tells for AI use." Word set drifts: "the word delve was famously overused by ChatGPT in 2023 and early 2024, but became less frequent later in 2024, then dropped off sharply in 2025." WP era list: mid-2025 on (GPT-5): "emphasizing, enhance, highlighting, showcasing". Kobak et al. (arXiv 2406.07016, abstract) measured "an abrupt increase in the frequency of certain style words" in 15 million PubMed abstracts. Promotional tone: WP, "LLMs have serious problems keeping a neutral tone" and "older LLMs (e.g., GPT-4) tend to output more blatantly positive text" [ref] "than newer LLMs, which are more subtly positive".
- Fix: Before: "Giải pháp toàn diện giúp nâng tầm thương hiệu." After: "Gói gồm 3 việc: audit, 2 bài/tuần, báo cáo tháng."
- Source: WP + paper (EN); quan sát thực tế (VI list). Detect: script (lexicon lists; the validator already has SLOP_HARD/SOFT).

### A3. Chuyển đoạn máy móc / mechanical transitions
- VI: "Hơn nữa", "Thêm vào đó", "Ngoài ra", "Tóm lại", "Nhìn chung", "Không thể phủ nhận rằng". EN: "Furthermore", "Moreover", "Additionally" at sentence start, "In conclusion", "Overall".
- Why AI: BVN: "các cụm từ chuyển đoạn khá máy móc như 'Hơn nữa', 'Thêm vào đó' ...; ... kết lại bài viết bằng cụm từ 'Tóm lại', 'Kết luận là...'". WP words to watch: "Additionally (especially beginning a sentence)".
- Fix: delete; let the content of the next paragraph do the joining. Before: "Hơn nữa, sản phẩm còn có 3 màu." After: "Có 3 màu."
- Source: BVN + WP. Detect: script (paragraph-initial regex).

### A4. Tránh "là" / avoidance of copula (EN mainly)
- EN: "serves as", "stands as", "represents a", "boasts", "features", "refers to" instead of "is/has". VI: "đóng vai trò là", "được xem là" in place of "là" (quan sát thực tế, weak).
- Why AI: WP: "LLM-generated text often replaces simple constructions that use copulas such as is or are with constructions such as serves as a or mark the."
- Fix: Before: "The report serves as a summary of Q3." After: "The report summarises Q3."
- Source: WP. Detect: script (EN regex), human (VI).

## B · Mẫu câu (sentence patterns)

### B1. "Không chỉ… mà còn / mà là" / negative parallelism
- VI: "Không chỉ là một chiếc bình, mà là tuyên ngôn phong cách." "Không phải X, mà là Y." EN: "Not just a bottle, but a style statement." "It isn't X, it's Y."
- Why AI: WP, Negative parallelisms: "While it is common among human writers ... it is stereotypically an 'AI sign.'" and "It is common for LLMs to use parallel constructions involving 'not', 'but', or 'however' such as 'Not only ... but ...' or 'It is not just ..., it's ...'." Also WP "Not X, but Y": "It's not ..., it's ...". BVN: "các chatbot AI cũng thường xuyên sử dụng cấu trúc câu 'không chỉ… mà còn…', 'tưởng chừng… nhưng…'". Owner names "không chỉ là… mà là…" as the pattern staff recognise instantly (quan sát thực tế).
- Fix: state the positive claim once. Before: "Không chỉ là chiếc bình, mà là tuyên ngôn phong cách." After: "Có 3 màu, khắc tên miễn phí."
- Source: WP + BVN + quan sát thực tế. Detect: script (regex; the current validator regex misses "không chỉ là … mà là", see RULES-PROPOSAL).

### B2. Mở bài rập khuôn / stock opener (rhetorical question, "Trong bối cảnh…")
- VI: "Bạn đã sẵn sàng cho một trải nghiệm mới?" "Trong bối cảnh ngành X đang phát triển không ngừng…" "Trong thế giới ngày nay…" EN: "Are you ready for…?" "In today's fast-paced world…"
- Why AI: BVN: "'Trong bối cảnh ngành [XYZ] đang phát triển không ngừng…' là một trong những kiểu câu mở đầu được AI ưa thích." Rhetorical opener: quan sát thực tế (the previous lesson listed it; WP does not treat it as a separate sign).
- Fix: open with the fact or the task. Before: "Bạn đã sẵn sàng…?" After: "Bình giữ nhiệt 500 ml, giá 290.000đ."
- Source: BVN + quan sát thực tế. Detect: script (paragraph-initial regex; "?" on a digit-free first sentence).

### B3. Kết bài rập khuôn, lời chat còn sót / stock closer and chat leftovers
- VI: "Hy vọng bài viết hữu ích!", "Chúc bạn thành công!", "Dưới đây là một số gợi ý…", "Bạn có muốn mình viết thêm…?" EN: "I hope this helps", "Certainly!", "Would you like…", "Here is a…", "let me know".
- Why AI: WP, Collaborative communication, words to watch: "I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., is there anything else, let me know, more detailed breakdown, here is a". BVN: "cách mở đầu quen thuộc 'Dưới đây là một số gợi ý…'". VI closers: quan sát thực tế.
- Fix: delete; end on the action the reader must take. Before: "Hy vọng caption này hữu ích!" After: "Đặt trước 30/9, giao trong 2 giờ."
- Source: WP (EN) + BVN + quan sát thực tế (VI). Detect: script (hard lexicon).

### B4. Câu dài đều nhau / uniform sentence rhythm
- VI/EN: every sentence 18-25 words, same subject-verb-adverb shape.
- Why AI: Shaib et al. code "Structure – Repetitive or templated sentence / formula pattern." Finhay blog (not research): "ChatGPT thường tạo ra các câu có độ dài tương đương nhau".
- Fix: vary length; one 4-word sentence per paragraph is enough.
- Source: paper (concept) + quan sát thực tế (VI). Detect: script+human (coefficient of variation of sentence length; experimental).

### B5. Câu đuôi "-ing" phân tích nông / superficial "-ing" tail (EN; VI "góp phần…", "khẳng định vị thế…")
- EN: "…, highlighting its commitment to quality." VI: "…, góp phần khẳng định vị thế thương hiệu."
- Why AI: WP, Superficial analyses: "AI chatbots tend to insert superficial analysis ... often done by attaching a present participle ('-ing') phrase at the end of sentences".
- Fix: cut the tail or replace with the measured effect. Before: "Chiến dịch đạt 2 triệu view, góp phần khẳng định vị thế thương hiệu." After: "Chiến dịch đạt 2 triệu view; brand recall tăng 6 điểm."
- Source: WP (EN) + quan sát thực tế (VI). Detect: script+human.

## C · Trình bày (formatting)

### C1. Xuống dòng sau mỗi câu / one sentence per paragraph
- VI/EN: 15 paragraphs, each a single sentence, no list structure.
- Why AI: quan sát thực tế (owner, 29/09/2026: "AI tools break lines after every sentence"). Related mechanism: Freeburg (arXiv 2603.27006, abstract) argues LLM prose carries "the structural orientation that LLMs acquire from markdown-saturated training corpora". Not in WP as a separate sign.
- Fix: group sentences that share one idea into 2-3 sentence paragraphs. Before: "Bình 500 ml.\n\nGiá 290.000đ.\n\nGiao 2 giờ." After: "Bình 500 ml, giá 290.000đ. Giao trong 2 giờ nội thành."
- Source: quan sát thực tế. Detect: script (run of ≥4 consecutive one-sentence paragraphs).

### C2. Gạch đầu dòng cho mọi thứ, "In đậm: giải thích" / bullets for everything, inline-header lists
- VI: "- Chất lượng: vượt trội.\n- Thiết kế: tinh tế.\n- Giá: hợp lý." EN: "• **Quality:** superior. • **Design:** refined."
- Why AI: WP, Inline-header vertical lists: "an ordered or unordered list where the list marker (number, bullet, dash, etc.) is followed by an inline boldfaced header, separated with a colon from the remaining descriptive text." BVN: "Chia nhỏ ý và liệt kê dạng bullet point. Đây là một trong những dấu hiệu điển hình của nội dung AI ... các ý này rất nông, thậm chí là sáo rỗng, và trùng lặp khá nhiều." Owner: AI overuses "-" bullets (quan sát thực tế). Freeburg: when told to avoid markdown, "overt features (headers, bullets, bold) are eliminated or nearly eliminated" — so a prompt instruction does remove this one.
- Fix: keep lists for real lists (prices, steps, deadlines); write reasoning as paragraphs. Before: the three bullets above. After: "Thân thép hai lớp, 3 màu, giá 290.000đ."
- Source: WP + BVN + quan sát thực tế. Detect: script+human (≥4 items, each ≤6 words and no digit = list of labels; house courses legitimately use `<li><b>Term</b>: …</li>` for definitions, so flag only label-lists).

### C3. In đậm tràn lan / overuse of boldface
- VI/EN: four bold phrases in a five-line paragraph; every occurrence of a keyword bolded.
- Why AI: WP: "AI chatbots may display various phrases in boldface for emphasis in an excessive, mechanical manner ... to emphasize every instance of a chosen word or phrase, often in a 'key takeaways' fashion. Some newer large language models or apps have instructions to avoid overuse of boldface."
- Fix: at most one bold phrase per paragraph, usually none.
- Source: WP. Detect: script (bold count inside `<p>` per 1k words; house courses measure median 4-7/1k, max 13.7/1k).

### C4. Tiêu đề cho đoạn hai câu, Viết Hoa Từng Chữ, emoji / headings over tiny sections, title case, emoji
- VI: "## 🚀 Lợi Ích Nổi Bật" above a two-sentence paragraph. EN: "## 🚀 Key Benefits".
- Why AI: WP, Title case: "In section headings, AI chatbots strongly tend to capitalize all main words." WP, Emoji: "they sometimes decorated section headings or bullet points by placing emoji in front of them ... while they are more rare now, they may still be seen." WP, Headings only containing other headings: "AI chatbots may generate a heading that only stores other headings, without text of their own." WP, Thematic breaks: "AI chatbots sometimes include a thematic break (----) between each section". WP, Markdown: "the default formatting style of most chatbots is Markdown".
- Fix: no heading for fewer than three paragraphs; sentence-case headings; no emoji in work documents.
- Source: WP. Note WP marks emoji as "more rare now". Detect: script (emoji regex; heading followed by <2 blocks; VI heading with ≥3 consecutive capitalised words).

### C5. Dấu gạch dài (—) / em dash
- VI: "Bình giữ nhiệt — người bạn đồng hành mỗi ngày — cho mọi hành trình." EN: "An insulated bottle — your everyday companion — for every journey."
- Why AI: WP: "LLM output uses them more often than nonprofessional human-written text of the same genre, and uses them in places where humans are more likely to use commas, parentheses, colons ... AI-generated em dashes are usually surrounded by spaces". **Now less common**: WP hatnote (September 2026): "If more recent examples of this AI sign can't be found, it should probably be moved to #Historical indicators, as it seems to be less common in current LLM output." and "A July 2026 study found that of contemporary models only Claude used em dashes more than professional writers, and ChatGPT used them less." Freeburg (abstract): "Em dash frequency and suppression resistance vary from 0.0 per 1,000 words (Llama) to 9.1 (GPT-4.1 under suppression)" and "even explicit em dash prohibition fails to eliminate the artifact in some models". BVN: "Nếu bạn thấy dấu gạch ngang này xuất hiện đến 2-3 lần trong một đoạn văn ngắn thì khả năng cao đó là nội dung AI." VnExpress 15/11/2025 reports OpenAI's update so ChatGPT follows a user instruction to avoid em dashes (`sources/vnexpress-chatgpt-em-dash.html`).
- Fix: comma, colon, or a new sentence. Before: "Bình giữ nhiệt — người bạn đồng hành mỗi ngày." After: "Bình giữ nhiệt dùng mỗi ngày."
- Source: WP + paper + BVN. Detect: script (count; spaced " — " is the AI-typical form). Keep in the lesson because Vietnamese typing rarely produces "—" at all, so any occurrence in VI staff copy is worth a look; label it "model mới dùng ít hơn".

### C6. Dấu ngoặc kép cong lẫn thẳng / curly quotes (EN, weak)
- Why AI: WP: "ChatGPT and DeepSeek typically use curly quotation marks ... Curly quotes alone do not prove LLM use." Word and macOS auto-curl quotes.
- Source: WP. Detect: script, low value. Not in the lesson.

## D · Nội dung (content)

### D1. Câu không có dữ kiện, lời hứa không kiểm được / no-fact sentence, uncheckable promise
- VI: "Ai dùng cũng sẽ yêu nó ngay từ lần đầu." EN: "Everyone who tries it will love it from day one."
- Why AI: Shaib et al. "Density – Many words, little information; filler or fluff." Kommers et al. "superficial competence". WP, Undue emphasis: "LLM writing often puffs up the importance of the subject matter"; WP, Superficial analyses.
- Fix: each sentence points to one fact. Before: "Ai dùng cũng sẽ yêu nó." After: "Đổi trả trong 7 ngày nếu không vừa ý."
- Source: paper + WP. Detect: human (a script can only flag sentences with no digit, no proper noun and a hype word).

### D2. Quy nguồn mơ hồ / vague attribution
- VI: "Các chuyên gia cho rằng…", "Nhiều nghiên cứu chỉ ra…", "Theo các báo cáo ngành…" EN: "Experts argue", "Industry reports", "Observers have cited", "studies show".
- Why AI: WP, Vague attributions: "AI chatbots tend to attribute opinions or claims to some vague authority—a practice called weasel wording. They also commonly exaggerate the quantity of sources". Words to watch: "Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications".
- Fix: name the source and the number, or cut the sentence. Before: "Các chuyên gia cho rằng màu đen bán chạy." After: "Khảo sát 120 khách tháng 8: 68% chọn màu đen."
- Source: WP (EN) + quan sát thực tế (VI). Detect: script (regex) + human (is a real source available?).

### D3. Bịa dữ kiện, bịa nguồn / fabricated facts and citations
- Why AI: BVN: "Đôi khi, AI sẽ bịa ra thông tin và nguồn trích dẫn không có thật." BVN tested 5 ChatGPT "ambient marketing" examples: "không có ví dụ nào là chính xác hoàn toàn". Shaib code "Factuality – Incorrect, fabricated, or misleading statement."
- Fix: facts come from the writer, in the prompt, before the words (the lesson's step 1). Not a "sign" in the lesson table; it is the reason for the method.
- Source: BVN + paper. Detect: human (fact check).

### D4. Lời từ chối trách nhiệm về kiến thức / knowledge-cutoff and source disclaimers
- EN: "As of my last knowledge update…", "While specific details are limited…", "should be treated as … rather than …". VI: "Tính đến thời điểm cập nhật của tôi…" (quan sát thực tế, rare in staff copy).
- Why AI: WP words to watch: "Up to my last training update, as of my last knowledge update, While specific details are limited/scarce..., not widely available/documented/disclosed". WP: "As of 2026, chatbots may also include disclaimers about how sources should be used".
- Fix: delete; check the fact yourself.
- Source: WP. Detect: script (hard lexicon). Not in the lesson (rare in the staff's output type).

### D5. Kết "thách thức và triển vọng" / outline-like "challenges and future outlook" ending
- EN: "Despite these challenges, X continues to…" VI: "Dù còn nhiều thách thức, X vẫn hứa hẹn…"
- Why AI: WP: "Many LLM-generated Wikipedia articles include a 'Challenges' section, which typically begins with a sentence like 'Despite its [positive/promotional words], [article subject] faces challenges...'".
- Source: WP (EN) + quan sát thực tế (VI). Detect: script (regex on "Despite these challenges", "Dù còn nhiều thách thức"). Not in the lesson.

---

## Which signs the sources say are fading (do not teach as certainties)
- Em dash: WP hatnote Sept 2026 "less common in current LLM output"; ChatGPT below professional writers per the July 2026 study WP cites; still above for Claude. Lesson keeps it with the note "Model mới dùng ít hơn".
- Emoji in headings/bullets: WP "more rare now".
- "delve" and the 2023-24 vocabulary: WP "dropped off sharply in 2025"; newer set is "emphasizing, enhance, highlighting, showcasing".
- Boldface: WP "Some newer large language models or apps have instructions to avoid overuse of boldface."
- Blatant superlatives: WP says newer models are "more subtly positive".
- Knowledge-cutoff disclaimers: tied to older fixed-cutoff models; source-usage disclaimers now take their place.


## Sources (fetched 29/09/2026)
- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (raw wikitext, 222,208 bytes)
- https://arxiv.org/abs/2601.06060 Kommers et al., Why Slop Matters (Dec 2025)
- https://arxiv.org/abs/2509.19163 Shaib et al., Measuring AI "Slop" in Text (v2 Jan 2026; full HTML also saved)
- https://arxiv.org/abs/2603.27006 Freeburg, The Last Fingerprint (Mar 2026)
- https://arxiv.org/abs/2406.07016 Kobak et al., excess vocabulary in PubMed abstracts (2024)
- https://help.brandsvietnam.com/vi/article/dau-hieu-nhan-biet-noi-dung-duoc-viet-boi-ai-3zy07d/ (VI, trade article)
- https://vnexpress.net/chatgpt-khac-phuc-dau-gach-ngang-dai-4964281.html (VI news, 15/11/2025)
- https://www.finhay.com.vn/en/meo-dung-chatgpt-khong-bi-van-mau-robotic (VI blog, 29/05/2026; SEO content, used only to confirm the VI phrase list is common knowledge)
- No Vietnamese peer-reviewed source on AI-written Vietnamese tells was found (searched 29/09/2026); VI lists stay "quan sát thực tế".

## Independent check (29/09/2026): corrections to apply when teaching
- A3 transitions ("Hơn nữa", "Moreover"): Wikipedia lists transition words under *Ineffective indicators* and "In conclusion / Overall" under *Historical indicators*. Weak on its own; mostly older models.
- C4 emoji: Wikipedia says emoji are "more rare now". C5 em dash: Wikipedia (Sept 2026 note) says it is "less common in current LLM output"; a July 2026 study it cites found Claude still above professional writers, ChatGPT below. Treat both as cues only alongside other signs.
- C1 one sentence per line and B2 rhetorical-question openers: no primary source; practitioner observation.
- Signs are edit cues, never proof of authorship; detectors have "non-trivial error rates" (Wikipedia).

## E · Dấu vết quy trình trong bản gửi người đọc (house rule, owner 29/09/2026)
Not research: the owner's rule, and the most common slop left by an AI-assisted verification workflow.
- Date stamps of the checking process in reader copy: "kiểm 28/09/2026", "(kiểm lại …)", "checked Sep 28, 2026", "đối chiếu lại nguyên văn …", "tính đến … (kiểm …)". Keep dates only when the date is the fact (effective date, release date, deadline).
- Evidence-status labels meant for the editor: "(quan sát thực tế)", "(in-house observation)", "(dấu hiệu yếu…)", "[S]", "SUPPORTED".
- Source lines listing everything consulted. Cite only the sources the reader can open and that carry the claim (e.g. "Nguồn: Wikipedia “Signs of AI writing”, Shaib và cộng sự (arXiv 2509.19163).").
- Caveats repeated inside every table row; state a shared caveat once, above the table.
