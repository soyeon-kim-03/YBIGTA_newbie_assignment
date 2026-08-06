# LLM Prompting 실험 보고서

- 모델: `llama-3.1-8b-instant` (Groq API), `temperature=0.0`
- 평가 데이터: `HuggingFaceH4/MATH-500` 중 Level 1–3, 4개 과목(Algebra, Intermediate Algebra, Number Theory, Counting & Probability) 필터링 후 앞 50문항
- Few-shot 예시: `HuggingFaceH4/MATH`의 **train split**에서 추출 (test 데이터 미사용)
- 채점: `math-verify`의 `parse`/`verify` + 정규화 문자열 비교

---

## 1. 정답률 비교

| Shot | Direct Prompting | CoT Prompting | My Prompting |
|:---:|:---:|:---:|:---:|
| 0-shot | 30% | 68% | **72%** |
| 3-shot | 42% | 60% | **68%** |
| 5-shot | 54% | **70%** | 66% |
| **평균** | 42.0% | 66.0% | **68.7%** |

My Prompting은 3개 구간 중 2개에서 CoT를 앞섰고, 평균 정답률에서도 가장 높았다. Direct Prompting은 전 구간에서 두 기법 모두에게 크게 뒤졌다.

### 오답 유형 분해

정답률만으로는 개선의 원인을 알 수 없어, 오답 50문항을 **파싱 실패**(답을 추출하지 못한 경우, `Predicted Answer: None`)와 **계산 오류**(답은 냈지만 틀린 경우)로 나누어 집계했다.

| 실험 | 오답 수 | 파싱 실패 | 계산 오류 | 기타 |
|:---|:---:|:---:|:---:|:---:|
| Direct 0-shot | 35 | 14 | 21 | – |
| Direct 3-shot | 29 | 12 | 17 | – |
| Direct 5-shot | 23 | 2 | 21 | – |
| CoT 0-shot | 16 | 7 | 9 | – |
| CoT 3-shot | 20 | 7 | 13 | – |
| CoT 5-shot | 15 | 5 | 10 | – |
| My 0-shot | 14 | 7 | 7 | – |
| My 3-shot | 16 | 5 | 10 | 1 |
| My 5-shot | 17 | 3 | 12 | 2 |

"기타"는 모델이 프롬프트의 출력 형식 예시인 `\boxed{ANSWER}`를 리터럴 문자열로 그대로 출력한 경우다 (아래 5절 참고).

---

## 2. CoT Prompting이 Direct Prompting보다 좋은 이유

0-shot 기준 30% → 68%로 38%p 차이가 났다. 예시를 전혀 주지 않은 조건에서 벌어진 격차이므로, 이는 few-shot 예시의 효과가 아니라 **추론 과정을 출력하도록 한 것 자체의 효과**다.

### 계산 과정을 외부화하여 단계적 조건부 확률을 만든다

Transformer는 토큰 하나를 생성할 때 고정된 깊이의 연산만 수행한다. Direct Prompting은 `Answer:` 직후에 최종 답을 요구하므로, 여러 단계가 필요한 문제의 모든 중간 계산을 단 한 번의 순전파 안에서 끝내야 한다.

반면 CoT는 중간 계산을 출력 토큰으로 내보내고, 그 토큰들이 다시 컨텍스트에 들어가 다음 단계의 입력이 된다. 즉 추론의 각 단계가 이전 단계의 결과를 명시적으로 조건으로 삼게 되어, 모델이 사용할 수 있는 실질적 연산 깊이가 늘어난다. 이는 Wei et al. (2022)이 CoT의 성능 향상 요인으로 제시한 메커니즘과 일치한다.

### 실제 응답에서 확인되는 차이

Q37 `(26² − 24² − 10)² − 10²`의 경우, Direct 5-shot은 `6300`을 냈다. 응답을 보면 `676 − 576 − 10 − 10`으로 10을 두 번 빼는 실수를 했는데, 답만 요구받았기 때문에 이 실수가 드러나지 않고 그대로 최종 답이 되었다. CoT 0-shot은 같은 문제에서 각 항을 나누어 계산하며 `8000`을 맞혔다.

Q19 다항식 나눗셈(`x⁶ − 3`을 `x + 1`로 나눈 몫)에서도 Direct는 0/3/5-shot 모두 실패했지만(각각 `None`, `... + x − 3`, `... + x − 2`), CoT 3-shot은 조립제법 과정을 적으며 정답을 냈다. 마지막 항만 틀리는 패턴은 중간 계산을 추적하지 않을 때 전형적으로 나타난다.

### 파싱 실패도 함께 줄어든다

Direct 0-shot에서 오답의 40%(14/35)가 답 추출 자체에 실패한 경우였다. 응답을 보면 `3T = S`, `CD = 29`, `\log_2 4^x = \log_2 2^8 \Rightarrow ...`처럼 식은 세웠지만 최종 값으로 정리하지 못한 채 끝난 사례가 많다. "설명 없이 답만 쓰라"는 지시가 오히려 모델이 정리되지 않은 중간 상태를 답 자리에 놓게 만든 것이다. CoT는 추론을 쓸 공간을 명시적으로 허용함으로써 이 문제를 완화했다(14 → 7).

### 한계: few-shot 수에 단조 증가하지 않는다

Direct는 30% → 42% → 54%로 shot 수에 따라 일관되게 상승했지만, CoT는 68% → 60% → 70%로 3-shot에서 오히려 떨어졌다. CoT의 few-shot 예시는 MATH train split의 실제 풀이(solution)를 그대로 쓰기 때문에, 어떤 문제가 뽑히느냐에 따라 예시 풀이의 스타일과 난이도가 크게 달라진다. 예시 3개는 이 분산을 평균내기에 표본이 작아, 특정 풀이 방식에 과도하게 끌려갔을 가능성이 있다. 3-shot에서 Q14, Q35, Q43, Q46 등이 파싱 실패로 무너진 것이 그 징후다.

---

## 3. My Prompting: 설계와 근거

### 설계 원칙

CoT의 오답을 위 표처럼 분해했을 때 병목이 두 가지로 나뉘었다. **파싱 실패**(CoT 평균 6.3건)와 **계산 오류**(CoT 평균 10.7건)다. 각각을 별개의 문제로 보고 따로 대응했다.

최종 프롬프트는 CoT의 단계적 추론을 유지하면서 다음을 추가한 것이다.

```
Instruction:
Solve the following mathematical question. Work step by step, taking as many
steps as the problem needs.

How to reason:
- Every step must make progress. Never rewrite a line you have already
  written, and never re-simplify an expression that is already simplified.
- Evaluate compactly: write 2^10 = 1024 rather than listing factors.
- Before boxing, check the sign, the number of digits, and that no term is missing.

Output rules (strict):
- The last line must be exactly: \boxed{ANSWER}
- Write nothing after the \boxed{} line.
- Always output \boxed{}, even if unsure or incomplete. Never end without it.
- Simplify first: evaluate powers and roots, reduce fractions, rationalize
  denominators. Write \frac{3}{2}, not 4^(3/2) or 1.5.
- Match the requested form: common fraction, simplest radical form,
  base subscript, or text.
```

Few-shot 예시는 CoT와 동일하게 train split의 풀이를 사용하되, 마지막 줄을 `\boxed{정답}` 단독으로 두어 "응답의 마지막 줄은 boxed"라는 패턴을 예시로도 학습시켰다.

### 각 규칙의 근거

**출력 형식 강제 (파싱 실패 대응).** CoT의 파싱 실패 응답을 직접 확인한 결과, 출력 길이 제한에 걸려 잘린 것이 아니라(최장 2,561자로 상한 미달) 모델이 결론을 내지 않고 계산만 나열하다 끝난 경우였다. 따라서 "불확실해도 반드시 `\boxed{}`로 끝낼 것"을 명시했다. 5-shot 기준 파싱 실패가 5건 → 3건으로 줄었다.

**표기 정규화 (파싱 실패 대응).** CoT에서 `4^(3/2)`처럼 값은 맞지만 요구된 형태가 아니어서 오답 처리된 사례가 있었다. 실제 오답에서 관찰된 표기를 규칙에 직접 예시로 넣었다.

**반복 금지 및 압축 평가 (계산 오류 대응).** 중간 실험에서 "모든 산술을 생략 없이 보이라"고 지시했더니, 모델이 `2 × 2 × 2 × ...`를 끝없이 나열하거나 "Simplify further"를 Step 6, 7, 8로 반복하며 진전 없이 응답을 끝내는 현상이 나타났다. 이를 막기 위해 "이미 쓴 줄을 다시 쓰지 말 것", "직접 평가 가능한 것은 압축해서 쓸 것"으로 바꿨다.

**출력 직전 점검 (계산 오류 대응).** CoT 오답에서 `2220` → `22200`(자릿수), `−256` → `−64`(거듭제곱), `x⁵−x⁴+x³−x²+x−1` → `... +x+3`(마지막 항)처럼 접근은 옳고 마지막에 미끄러진 사례가 반복됐다. 부호·자릿수·누락항 세 가지로 점검 대상을 구체적으로 한정했다.

### CoT보다 나을 수 있는 이유

CoT의 핵심 지시는 "단계적으로 생각하라"이며, **추론 과정에만** 개입한다. 답이 어떤 형태로 나와야 하는지, 계산이 언제 끝나야 하는지는 규정하지 않는다. My Prompting은 추론 방식은 CoT를 그대로 유지하면서 **출력 계약(output contract)과 종료 조건**을 추가로 명시한 것이다.

이 차이가 0-shot에서 가장 크게 나타났다(68% → 72%). 예시가 없으면 모델은 형식을 추론할 근거가 전혀 없으므로, 지시문이 형식을 직접 규정하는 것의 이득이 가장 크다. 오답 분해에서도 계산 오류가 9건 → 7건, 전체 오답이 16건 → 14건으로 줄었다.

특히 Q3(asymptote 코드로 그려진 그래프에서 평균 속도가 가장 빠른 학생을 고르는 문제)은 Direct·CoT 전 구간에서 모두 오답이었으나 My Prompting 0-shot과 3-shot에서 정답(`Evelyn`)을 맞혔다. `\text{}` 형태의 텍스트 답까지 요구 형식에 포함시킨 규칙이 작동한 것으로 보인다.

---

## 4. 실패한 시도들

성능이 오른 최종안만큼이나, 오르지 않은 시도에서 얻은 것이 있어 함께 기록한다. 아래는 모두 0-shot 기준이다.

| 버전 | 길이 제약 | 파싱 실패 | 계산 오류 | 정답률 |
|:---|:---|:---:|:---:|:---:|
| Plan–Solve–Check, 12줄 제한 | 강함 | 3 | 19 | 56% |
| 8단계 상한 | 중간 | 5 | 16 | 58% |
| 제약 없음 (최종안) | 없음 | 7 | 7 | **72%** |

일관된 경향이 관찰된다. **출력 길이를 조이면 파싱 실패는 줄지만 계산 오류가 그보다 크게 늘어난다.** 길이 제한은 모델이 답을 빨리 내도록 강제하므로 `\boxed{}`에는 잘 도달하지만, 정작 계산에 쓸 공간을 빼앗는다. 파싱 실패 1건을 줄이는 대가로 계산 오류가 2~3건 늘어 순손실이었다.

또한 초기 버전에 넣었던 Plan(계획 서술) 단계와 사후 Check(재검토) 단계는 도움이 되지 않았다. 8B 규모 모델은 자신의 풀이를 독립적으로 재검증할 능력이 약해, 맞은 답을 재검토하다 틀린 답으로 바꾸는 경우가 관찰됐다. 최종안에서는 Check를 "답을 쓰기 직전 부호·자릿수·누락항만 확인"으로 축소했다.

---

## 5. 관찰된 부작용

My Prompting에서 모델이 출력 규칙의 자리표시자인 `\boxed{ANSWER}`를 리터럴 문자열로 그대로 출력한 사례가 3건 발생했다(3-shot 1건, 5-shot 2건). 형식 지시를 강하게 줄수록 모델이 그 예시 자체를 모방 대상으로 삼을 수 있음을 보여준다. `ANSWER` 대신 실제 답이 들어간 구체적 예시를 쓰거나, 자리표시자를 명시적으로 구분했다면 피할 수 있었을 것이다.

5-shot에서 성능이 66%로 가장 낮았던 것도 이와 관련이 있을 수 있다. 예시가 많아질수록 지시문의 상대적 비중이 줄어드는 한편, 형식 규칙과 few-shot 예시의 스타일이 충돌할 여지도 커진다.

---

## 6. 실험 환경 및 재현성

- 모든 실험은 동일한 50문항(필터링된 `math_test`의 앞 50개)에 대해 수행했다.
- `temperature=0.0`으로 고정했다.
- few-shot 예시 추출에 `random.Random(seed + num_examples)`로 시드를 고정하여, 같은 shot 수에 대해 항상 동일한 예시가 뽑히도록 했다.
- API 호출 결과를 `llm_cache.jsonl`에 저장하여, 동일 프롬프트 재실행 시 캐시를 재사용하도록 했다. Groq 무료 티어의 분당 토큰 제한(TPM 6,000)에 맞춰 슬라이딩 윈도우 방식으로 요청 속도를 조절했다.
- CoT few-shot 예시는 풀이 길이 700자 이하이고 `[asy]` 그래프 코드를 포함하지 않는 문제로 한정했다. 토큰 사용량을 줄이고, 텍스트만으로 재현 불가능한 예시가 들어가는 것을 막기 위함이다.