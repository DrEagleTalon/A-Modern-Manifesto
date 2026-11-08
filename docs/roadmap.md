# Roadmap

Which works come next, and what can legally go into a public repository. Copyright, more than length, decides the order.

The live queue is [`catalog.yaml`](../catalog.yaml): every work's priority, citation prefix, rights tier, stage and source locations. The table in the main README is generated from it on every build. This page explains the reasoning behind the tiers; when the two disagree, `catalog.yaml` wins.

**This is a working guide, not legal advice.** "PD" means public domain in the United States, where GitHub hosts the repository. Every entry marked *check* needs its specific edition verified before the full text goes in. A translation has its own copyright, separate from the original.

## Tier A: original and an English translation both public domain

These can go in complete, with a historical English column.

| Work | Original | Historical English | Notes |
|---|---|---|---|
| ~~Communist Manifesto~~ (1848) | German | Moore and Engels, 1888 | in the library (`CM`) |
| ~~Wage Labour and Capital~~ (1849) | German | Lothrop, 1902 | in the library (`WLC`) |
| Value, Price and Profit (1865) | **English** (Marx's own) | none needed | Original is English, so there is only an original column and a modern one |
| The Civil War in France (1871) | **English** (Marx's own) | none needed | Same |
| Socialism: Utopian and Scientific (1880) | French/German | Aveling, 1892 | |
| The Eighteenth Brumaire (1852) | German | De Leon, 1898 | |
| The Origin of the Family, Private Property and the State (1884) | German | Untermann, 1902 | |
| The Condition of the Working Class in England (1845) | German | Wischnewetzky, 1887 | Long |
| The Poverty of Philosophy (1847) | French | Quelch, 1900 | |
| Kropotkin, The Conquest of Bread (1892) | French | 1906 English edition | |
| Kropotkin, Mutual Aid (1902) | **English** | none needed | |
| Kropotkin, The State: Its Historic Role (1896) | French | Freedom Press, 1898 | |
| Malatesta, Anarchy (1891) | Italian | Freedom Press, 1890s | |
| Bakunin, God and the State (1882) | French | Tucker, 1883 | |
| Goldman, Anarchism and Other Essays (1910) | **English** | none needed | |
| Berkman, Now and After: The ABC of Communist Anarchism (1929) | **English** | none needed | 1929 US works became PD on 1 January 2025 |
| Bebel, Woman and Socialism (1879) | German | Meta Stern, 1910 | |
| IWW Preamble (1905/1908), The Miners' Next Step (1912) | **English** | none needed | Short, good for a first contribution |
| Mary Marcy, Shop Talks on Economics (1911) | **English** | none needed | |

## Tier B: original public domain, English translation needs checking

The original can go in. Use a pre-1930 English translation where one exists; otherwise the modern column is translated straight from the original and the historical English column stays empty.

| Work | Original | Status of English |
|---|---|---|
| Engels, Principles of Communism (1847) | German, PD | Standard English (Sweezy, 1952) is likely protected. Translate from the German. |
| Marx, Critique of the Gotha Programme (1875) | German, PD | *check* early English editions |
| Marx and Engels, The German Ideology (1845-46) | German, PD | English editions from the 1930s onward, *check* |
| Lenin, The State and Revolution (1917) | Russian, PD | 1919 English editions likely PD, *check*; Progress Publishers versions uncertain |
| Lenin, Imperialism (1917), What Is to Be Done? (1902) and other works | Russian, PD | *check* each translation |
| Luxemburg, Reform or Revolution (1899) | German, PD | 1937 English, *check* |
| Luxemburg, The Mass Strike (1906) | German, PD | 1925 English (Lavin), likely PD, *check* |
| Bakunin, Statism and Anarchy (1873) | Russian, PD | Modern English (1990) is protected. Translate. |
| Trotsky, various (1920s-30s) | Russian, PD in many countries, *check* US status | 1930s English translations, *check* |

Russian, French and Italian originals need a sentence splitter tuned for each language (`scripts/lib/segment.py`) before ingest.

## Tier C: still under copyright

These cannot go into a public repository in full. The library can host commentary, short quotations, study guides and adaptations that point readers to a legal edition.

| Author | Why |
|---|---|
| Mao Zedong | Protected in the US for 95 years from each publication (into the 2030s and beyond). In China his works enter the public domain on 1 January 2027. |
| Frantz Fanon, Walter Rodney, C.L.R. James, Harry Haywood, Paul Baran, Harry Braverman, Michael Harrington, Che Guevara | Authors died after 1955; works protected |
| Pannekoek, Workers' Councils (1946); Rocker, Anarcho-Syndicalism (1938); Einstein, "Why Socialism?" (1949) | *check*: protection depends on country and on US renewal |

## Suggested order

1. **Value, Price and Profit**: English original, short, and the natural companion to WLC for the pamphlet "Who Profits From Your Work?".
2. **Principles of Communism**: short, the Manifesto's draft, and a good test of translating with no historical English.
3. **IWW Preamble and The Miners' Next Step**: very short English originals, so new contributors can learn the workflow on them.
4. **Socialism: Utopian and Scientific**.
5. **Kropotkin, The Conquest of Bread** and **Malatesta, Anarchy**: so the library is not only Marxist from the start.
6. **Lenin, The State and Revolution**: once a Russian splitter is in place and the 1919 English is checked.
7. **Luxemburg, The Mass Strike**.

Adaptations can start for any tier, including Tier C, as long as they quote briefly and cite.
