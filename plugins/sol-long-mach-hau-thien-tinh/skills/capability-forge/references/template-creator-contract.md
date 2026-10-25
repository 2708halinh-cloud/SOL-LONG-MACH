# Template Creator Contract

Use Template Creator for a reusable artifact-template skill backed by a document, presentation, spreadsheet, Google Workspace artifact, image, email, Slack message, or Site source.

Do not use Template Creator as a substitute for Plugin Creator when the requested outcome is a plugin skill, capability router, connector behavior, or plugin metadata/asset update.

When Template Creator is callable and a reusable artifact template is genuinely needed:
1. retain the exact reference/source identity;
2. treat linked Google Workspace sources as read-only references;
3. generate a representative preview through the supported workflow;
4. preserve native structure and source URL;
5. never claim the template installed until the product confirms save / the user accepts Save changes.

When Template Creator is not callable in the current session, record `TEMPLATE_CREATOR = UNAVAILABLE_THIS_SESSION` and continue other authorized capability work that does not require it. Do not hand-author a fake artifact-template package.
