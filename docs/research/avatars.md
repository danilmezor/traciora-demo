# Avatar sources for fictional demo contacts (research, 2026-11-13)

Pages were read through a page-to-text fetch tool (summarised by a small model), so quotes are as returned by it, not byte-checked. Anything not read on a licence page is marked unverified. Not legal advice; a lawyer should read the points flagged "lawyer".

## 1. Photographs of real people

### Unsplash - https://unsplash.com/license (no date or version on page)
- "Commercial and non-commercial purposes"; "No permission needed (though attribution is appreciated!)".
- "This license does not include the right to compile images from Unsplash to replicate a similar or competing service." Cannot sell images without significant modification.
- Identifiable people: page is silent (unverified elsewhere). Model-release status of portraits is not guaranteed by the licence.
- Bundling in a private repo/app: not stated as prohibited; the compile clause targets competing services. Lawyer.
- Verdict: unsafe for faces of fictional (negative) characters; fine for non-face pictures.

### Pexels - https://www.pexels.com/license/ (no date; footer 2026)
- "Attribution is not required."
- "Identifiable people may not appear in a bad light or in a way that is offensive."
- "Don't imply endorsement of your product by people or brands on the imagery."
- "Don't redistribute or sell the photos and videos on other stock photo or wallpaper platforms."
- Verdict: an angry customer / fired-for-theft character using a real face breaks the bad-light rule directly. Not for faces. Non-face OK.

### Pixabay - https://pixabay.com/service/license-summary/ and https://pixabay.com/service/terms/ ("Last updated: 20 October, 2026")
- "Use Content for free"; "without having to attribute the author."
- "You cannot sell or distribute the Content (either in digital or physical form) on a Standalone basis."
- "You cannot use Content in any immoral or illegal way, especially Content which features a recognisable person."
- "You cannot use any Content on or in conjunction with anything pornographic, obscene, offensive".
- Section 8: "The compilation of the Content is copyrighted as a collective work and/or compilation" (under Use of the Service, not the content licence).
- Bundling: standalone-distribution ban; image files inside a private repo shown in an app is not standalone, but shipping the dataset to others could be. Lawyer.
- Verdict: no real faces. Non-face OK.

### Wikimedia Commons - https://commons.wikimedia.org/wiki/Commons:Photographs_of_identifiable_people
- "All images hosted on Commons must allow free commercial reuse from a copyright point-of-view, but the subject of the photograph may still refuse permission or demand payment for such reuse."
- "[The right of publicity] is only likely to affect advertising/commercial re-users of the image."
- "The subject may have additional legal rights, over and above those enforced here, which may restrict certain re-uses." The {{Personality rights}} template warns re-users.
- Verdict: copyright-free is not person-free; marketing use is exactly the risky case. Reject for faces.

## 2. Faces of people who do not exist

### Generated Photos - https://intercom.help/generated-photos/en/articles/7872726-generated-photos-terms-and-conditions (dated October 16, 2023); free-use FAQ https://intercom.help/generated-photos/en/articles/7241309-can-i-use-your-synthetic-humans-for-free
- Free: "Permission is granted to download one copy of Materials from the Website for personal, non-commercial usage only." "You can use free synthetic humans in non-commercial projects only." Attribution link "Photos by Generated.Photos" required.
- Paid: "a perpetual license to the Materials is granted" for use "in one project".
- Prohibited: "Redistribute or resell the Materials"; API: "Caching, stockpiling, or downloading Materials as stand-alone files" and "Compiling datasets"; may not distribute a final product "in a manner allowing" others to extract Materials as stand-alone files.
- Prohibited uses: "For defamation, disparaging, harassment, discrimination, or promotion of violence or hatred."; may not "create or disseminate verifiably false or misleading information."
- Verdict: free tier is non-commercial, so a prospect demo is out; paid needs a read on "disparaging" for the thief character and on 2,000 images in one project. Cost unverified (pricing not read).

### thispersondoesnotexist.com - https://thispersondoesnotexist.com/
- Page carries no licence, terms or copyright statement (only a domain-for-sale notice). No licence means no grant. Model is NVIDIA StyleGAN2, code under "Nvidia Source Code License-NC" (https://github.com/NVlabs/stylegan2/blob/master/LICENSE.txt): use "non-commercially", defined as "for research or evaluation purposes only". Whether that covers outputs: the page does not say. Lawyer.
- FFHQ training set https://github.com/NVlabs/ffhq-dataset: real Flickr photos "under either Creative Commons BY 2.0, Creative Commons BY-NC 2.0, Public Domain Mark 1.0, Public Domain CC0 1.0,..." "All of these licenses allow free use, redistribution, and adaptation for non-commercial purposes." Dataset metadata CC BY-NC-SA 4.0. Real people's faces are in the training data; generated faces can occasionally resemble training faces (not on the pages; general knowledge, unverified).
- Verdict: no licence; do not use.

### Open synthetic-face datasets
- SFHQ (~425,000 1024x1024 faces, "high degree of variability on the axes of identity, ethnicity, age, pose, expression") https://github.com/SelfishGene/SFHQ-dataset: "Since all images in this dataset are synthetically generated there are no privacy issues or license issues surrounding these images." Repo shows MIT; no image licence text read; Kaggle licence field not readable. Generated by StyleGAN2/diffusion models trained on FFHQ-like data (upstream licences inherit unclear terms). Verdict: best volume and diversity, but licence unverified and the statement is the author's own, not a grant. Lawyer.
- SynthPar (search result only, MIT, unverified), Face Synthetics (non-commercial research, search result), 140k Real and Fake Faces (no licence stated). No clearly CC0 StyleGAN human-face set found.
- Gwern anime faces are CC0 but anime, not suited.

### US legal status of AI-generated images
- US Copyright Office, Copyright and AI Part 2 (2025-01-29): copyright needs human authorship; prompts alone are not enough. So a raw output is likely uncopyrighted and needs no licence from the generator's user, but the generator's terms (contract) and the model licence still can bind. Read via search summaries only (unverified against the report). Lawyer for contract-vs-copyright and likeness questions.

## 3. Illustrated or abstract avatars

### DiceBear - https://www.dicebear.com/licenses/
- Code: "The source code in the dicebear/dicebear repository is available under the MIT license." 61 styles.
- CC0 1.0 (42): Blobs, Cameo, Clay, Constellation, Critters, Cutouts, Disco, Gaze, Glass, Identicon, Initial Face, Initials, Landscape, Line Face, Loops, Lorelei (+Neutral), Marbles, Moods, Notionists (+Neutral), Open Peeps, Patchwork, Pixel Art (+Neutral), Pixelbot, Planets, Rings, Shadows, Shape Grid, Shapes, Slice, Sprouts, Squircles, Stack, Stripes, Thumbs, Triangles, Voxel Art, Voxel Bot, Waves, Weave.
- CC BY 4.0 (14, attribution needed): Adventurer, Big Ears, Big Smile, Croodles, Dylan, Fun Emoji, Glyphs, Micah, Miniavs, Personas, Toon Head (+Neutral variants).
- MIT: Icons. Artist's own terms (free for personal and commercial per the page): Avataaars, Bottts.
- Seeded and deterministic: unlimited distinct avatars. Cartoon faces depict no real person. Verdict: safest scripted option. Use CC0 styles only (Lorelei, Notionists, Open Peeps, Thumbs) to avoid attribution.

### Open Peeps - https://www.openpeeps.com/
- "Free for commercial and personal use under CC0 License." Pablo Stanley. Hand-drawn people; no avatar-set licence conflict.

### Notionists (via DiceBear) - https://www.dicebear.com/styles/notionists/
- "This avatar style is a remix of: Notionists by Zoish, licensed under CC0 1.0."

### Boring Avatars - https://github.com/boringdesigners/boring-avatars
- Sidebar: MIT (licence text not read). Abstract SVGs from strings (marble, beam, pixel, sunset, ring, bauhaus). Not people.

### Multiavatar - https://raw.githubusercontent.com/multiavatar/Multiavatar/main/LICENSE
- "MULTIAVATAR LICENSE v1.0": "Permission is hereby granted, free of charge, including for commercial purposes." But "This license does not include the right to replicate a similar or competing product/service", "It is not allowed to re-package the existing set of avatar designs", must remain "an addition to your product." Verdict: skip; DiceBear CC0 is cleaner.

## 4. Non-face pictures (cars, pets, landscapes)
Unsplash, Pexels and Pixabay are all usable: no person is shown, so the identifiable-person clauses do not bite. Pexels and Unsplash need no attribution; Pixabay also none. Check each image for visible people, brand logos and licence plates (not in the licence pages; general caution). Keep files in the private repo; do not publish the image set as a standalone download (Pixabay standalone clause, Unsplash compile clause, Pexels redistribute clause). Count: all three libraries hold millions of images (not read from the pages, unverified).

## Recommendation
1. No picture (about a third): zero risk, zero cost; also realistic since many messenger users have none. Use initials.
2. Non-face photos (about a third): pets, cars, landscapes from Pexels or Unsplash (or Pixabay); download about 700 via their APIs (API terms not read, unverified), store with source URL and licence per file.
3. Illustrated faces (about a third) via DiceBear CC0 styles, seeded by contact id: no real person, scripted, no attribution, any market. Works for negative characters.
4. Synthetic photoreal faces only if a lawyer clears a source: Generated Photos paid licence, or SFHQ (author-asserted licence-free, ethnicity-diverse, so US and Russian-looking faces can be picked via classifier, effort not assessed). Not thispersondoesnotexist.
5. Never real-person stock portraits for named, negatively portrayed characters (Pexels bad-light rule; Wikimedia personality rights).

## Not read
Pexels, Unsplash licence dates (none on page); Pixabay summary page date; Generated Photos pricing and free-faces library size; SFHQ image licence text and Kaggle licence field; Boring Avatars LICENSE; Copyright Office report itself; Stock API terms; Hugging Face dataset cards.
