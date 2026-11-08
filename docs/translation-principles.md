# Translation principles

These are the house rules for the `modern` column in every work. They exist so that thousands of verses translated by many hands still read as one library. Change them through a Discussion, not in a pull request that also changes verses.

## 1. The original is the source

Translate from the original language. The historical English translations are witnesses, not sources. Some, like the 1888 Manifesto, were revised by Engels himself and still adapt freely for their readers; others, like Lothrop's 1902 *Wage-Labor and Capital*, change money, reorder sentences and smooth the argument. Where the historical English departs from the original, the modern text follows the original and the departure is noted.

Example: in `CM II.67.1` the 1888 English adds "necessitate further inroads upon the old social order", which is not in the German.

When a work exists in more than one authorial version (WLC 1849 and 1891), translate the version the work's `work.yaml` names as the base text and show the other in notes.

## 2. Faithful first, then readable

A reader today should be able to follow every sentence on a first reading. That is achieved by plain word choice and sentence structure, never by changing what is claimed. If a sentence can only be made clear by adding information, the information goes in `notes`.

Long German periods may be broken into shorter English sentences. Use `joined_to` (see VERSIFICATION.md) when one modern sentence covers two German verses.

## 3. Do not update the argument

Each work is a historical document. As Marx and Engels wrote of the Manifesto in 1872 (`CM P1872.3.1`), they no longer had the right to alter it, and neither do we. The modern draft keeps the original claims, including the ones that history has complicated and the ones a modern reader will find offensive. Commentary, data and later developments belong in `notes`, the glossary, or readings.

## 4. Do not sanitize, do not sharpen

Translate harsh words as harsh and mild words as mild. "Despotische Eingriffe" (`CM II.67.1`) stays despotic. The 19th-century vocabulary of "barbarian" and "civilised" nations (`CM I.22.2`, `CM I.23.3`) is translated as what it is, and a note explains it, including the anti-colonial critique of that framing. Do not make the authors more radical or more moderate than the German.

## 5. Terms of art are decided once

Recurring terms are settled in the work's `glossary.yaml` and used consistently across works where the same German word appears. Until an entry is marked `decided`, use the term in the entry's `interim` field and add a note if you think it is wrong.

## 6. People, not men

German *Arbeiter* and *Menschen* are grammatically masculine but generic. Use "workers" and "people" unless the German refers to men specifically. The famous closing line is a separate glossary decision.

## 7. Names, titles, quotations

- Keep personal names in their usual English form, with the German in notes if they differ (Grün and Gruen).
- Titles of works: English title if a standard one exists, original in notes.
- Where the authors quote someone, translate the quotation and say in `notes` who is being quoted and from where.

## 8. Register

Plain, serious, spoken English. Readable aloud at a meeting. No academic jargon that the German does not use, no internet slang, no phrasing that will date in five years. Avoid em dashes; use commas, parentheses or a new sentence.

## 9. Translation is not adaptation

Modern examples, today's money, today's workplaces and updated statistics belong in `adaptations/`, never in the `modern` column. A reader of the modern draft must be able to trust that it says what the original says.

## 10. Notes

`notes` is for short, sourced remarks: what a term meant in 1848, a variant reading between editions, a historical reference, a cross-reference to another verse. Arguments longer than a few sentences go to a Discussion and the note links to it.
