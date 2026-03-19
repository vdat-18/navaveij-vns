"""Output Schema Enricher for adding system-injected fields to AI output."""

from loguru import logger


class OutputEnricher:
    """Enriches AI output with system-injected fields from Signal Store and Ruleset Store."""

    def enrich_add_ons(self, ai_add_ons: list[dict], ruleset_add_on_library: list[dict]) -> list[dict]:
        """Enrich add-on items with Ruleset Store metadata.

        Args:
            ai_add_ons: AI-generated add-on items with item_code and priority_level
            ruleset_add_on_library: Full add-on library from Ruleset Store

        Returns:
            Enriched add-on items with label, category, navavej_product, trigger_signals_matched
        """
        enriched = []

        # Create lookup map from item_code to add-on item
        add_on_map = {item.get("item_code"): item for item in ruleset_add_on_library}

        for ai_add_on in ai_add_ons:
            item_code = ai_add_on.get("item_code")
            if not item_code:
                logger.warning(f"Add-on missing item_code: {ai_add_on}")
                continue

            ruleset_item = add_on_map.get(item_code)
            if not ruleset_item:
                logger.warning(f"Add-on item_code not found in Ruleset Store: {item_code}")
                enriched.append(ai_add_on)
                continue

            # Enrich with Ruleset Store metadata
            enriched_item = {
                **ai_add_on,
                "label": ruleset_item.get("label", item_code),
                "category": ruleset_item.get("category", "other"),
                "navavej_product": ruleset_item.get("navavej_product", {}),
                "trigger_signals_matched": self._find_matched_signals(
                    item_code, ruleset_item, ai_add_on.get("supporting_signals", [])
                ),
            }

            enriched.append(enriched_item)

        return enriched

    def _find_matched_signals(self, item_code: str, ruleset_item: dict, supporting_signals: list[str]) -> list[str]:
        """Find which trigger signals from Ruleset Store matched the supporting signals.

        Args:
            item_code: Add-on item code
            ruleset_item: Full add-on item from Ruleset Store
            supporting_signals: Signals that AI used to justify this add-on

        Returns:
            List of trigger signal IDs that matched
        """
        trigger_signals = ruleset_item.get("trigger_signals", [])
        matched = [sig for sig in trigger_signals if sig in supporting_signals]

        logger.debug(f"Add-on {item_code}: {len(matched)}/{len(trigger_signals)} trigger signals matched")

        return matched

    def enrich_output(
        self,
        ai_output: dict,
        clinical_signals: dict,
        ruleset_response: dict,
        signal_store_meta: dict,
    ) -> dict:
        """Enrich complete AI output with system-injected fields.

        Args:
            ai_output: Raw AI output from BAML
            clinical_signals: Clinical signals from Signal Store
            ruleset_response: Program ruleset response from Ruleset Store
            signal_store_meta: Metadata from Signal Store (_meta section)

        Returns:
            Fully enriched output matching Recommendation Output Schema
        """
        enriched = {
            **ai_output,
            # System-injected fields
            "rule_preliminary_tier": clinical_signals.get("rule_preliminary_tier", "Standard"),
            "resolved_package": ruleset_response.get("resolved_package", {}),
            "recommendation_source": "AI",
            "patient_high_alert": len(clinical_signals.get("missing_signals", [])) > 5,
            "metadata": {
                "ruleset_version": ruleset_response.get("ruleset_version", ""),
                "computed_at": ruleset_response.get("computed_at", ""),
            },
        }

        # Enrich add-ons
        if "add_ons" in ai_output:
            enriched["add_ons"] = self.enrich_add_ons(ai_output["add_ons"], ruleset_response.get("add_on_library", []))

        return enriched
