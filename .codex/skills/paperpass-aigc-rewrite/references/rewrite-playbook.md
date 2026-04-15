# Rewrite Playbook

## Goal

Lower AIGC-like sentence risk without damaging thesis style.

Target:

- keep terminology professional
- keep facts and numbers unchanged
- remove template-like sentence shapes
- add only concrete, local detail

## Unsafe Patterns

### 1. Connector chain

High risk markers:

- `因此`
- `此外`
- `与此同时`
- `结果表明`
- `这意味着`
- `可以看出`
- `需要注意的是`
- `从应用角度看`
- `具体而言`
- `换言之`
- `基于此`

Unsafe shape:

`现象 + 因此 + 解释 + 结论`

Safer move:

- split into two or three shorter sentences
- keep the observation sentence separate from the interpretation sentence
- remove one connector first, not all terminology

### 2. Figure conclusion chain

Unsafe shape:

`图X显示... 说明... 提示... 因此...`

Safer move:

- sentence 1: state what appears in the figure
- sentence 2: state what can be retained as an observation
- sentence 3 only if needed: add a restrained interpretation

Do not jump from figure to mechanism in one sentence.

### 3. Metric summary template

Unsafe shape:

`最优模型为... 准确率... F1... 说明...`

Safer move:

- keep the best model and metrics
- separate the metric report from the interpretation
- use a narrower conclusion:
  - `在当前样本下`
  - `在该验证设置下`
  - `就本实验而言`

### 4. Dense term cluster

Unsafe shape:

`EEG / fMRI / BOLD / ROI / 融合 / 网络 / 指标 / 分类` packed into one long sentence

Safer move:

- keep the key terms
- reduce the number of terms per sentence
- assign each sentence one main job:
  - modality difference
  - feature organization
  - result interpretation

### 5. Generic outlook paragraph

Unsafe shape:

`样本量不足 + 未来验证 + 实际应用 + 迁移可能性`

Safer move:

- keep one concrete limitation per sentence
- keep one concrete future direction per sentence
- avoid “大而全”的总结句

## Safe Expansion

Expansion is allowed only when it adds local detail.

Good expansion sources:

- sample count
- channel count
- ROI source
- block length / window length
- nested cross-validation setting
- exact metric meaning
- why this dataset needs this design

Bad expansion:

- empty background filler
- broad textbook explanation unrelated to the current experiment
- generic “important / meaningful / valuable” wording

## Safe Sentence Shapes

### Observation first

Unsafe:

`图4-5显示... 这意味着联合反馈更优。`

Safer:

`图4-5中，eegfmriNF在多数任务窗口里处于较高区间。这个现象与静态结果方向一致。`

### Narrow interpretation

Unsafe:

`结果表明该方法具有显著优势。`

Safer:

`在当前样本和验证设置下，该组合取得了更高的准确率和F1。`

### Split theory and result

Unsafe:

`由于EEG具有高时间分辨率而fMRI具有高空间分辨率，因此融合后性能提升。`

Safer:

`EEG更容易捕捉任务期间的节律变化。fMRI补入了空间侧化信息。在当前实验中，两类信息组合后取得了更高的分类表现。`

## Rewrite Checklist

For each high-risk sentence:

1. Keep:
   - numbers
   - model names
   - dataset facts
   - chapter logic

2. Remove or weaken:
   - summary connectors
   - full-sentence causal leaps
   - one-sentence figure-to-mechanism jumps

3. Rebuild:
   - split long sentences
   - one sentence, one main function
   - add local detail if a sentence becomes too short

4. Final pass:
   - no colloquial language
   - no fabricated facts
   - no generic filler
   - no repetitive summary templates
