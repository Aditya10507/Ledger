import { test, expect } from "@playwright/test";
import path from "path";

const FIXTURES = path.resolve(__dirname, "../../test_data/test_data");

// Helper: login as analyst
async function login(page: any) {
  await page.goto("/login");
  await page.fill("#login-email", "analyst@ledger.demo");
  await page.fill("#login-password", "password123");
  await page.click('button:has-text("Log in")');
  await page.waitForURL("**/dashboard", { timeout: 10_000 });
}

// Helper: navigate to New Run and upload both files via the file inputs
async function uploadFiles(
  page: any,
  ledgerPath: string,
  settlementPath: string
) {
  await page.goto("/runs/new");
  // FileDropZone has hidden <input type="file"> elements
  const fileInputs = page.locator('input[type="file"]');
  await fileInputs.nth(0).setInputFiles(ledgerPath);
  await fileInputs.nth(1).setInputFiles(settlementPath);
}

// ============================================================
// VALID DATASETS
// ============================================================

test.describe("Valid Datasets", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("CLEAN: clean_ledger + clean_settlement → 5 matched, 0 flagged", async ({
    page,
  }) => {
    await uploadFiles(
      page,
      path.join(FIXTURES, "valid/clean_ledger.csv"),
      path.join(FIXTURES, "valid/clean_settlement.csv")
    );

    await page.click('button:has-text("Run Reconciliation")');

    // Should navigate to Run Summary page
    await page.waitForURL("**/runs/**", { timeout: 15_000 });

    // Wait for Run Summary to load
    await expect(page.locator("h1:has-text('Run Summary')")).toBeVisible({
      timeout: 10_000,
    });

    // Verify stats: Total Records = 5
    await expect(page.locator("text=Total Records")).toBeVisible();
    await expect(page.locator("text=5")).toBeVisible();

    // Navigate to Flags page
    await page.click('a:has-text("View Flags")');
    await page.waitForURL("**/runs/**/flags", { timeout: 10_000 });

    // Verify empty state — no anomalies
    await expect(
      page.locator("text=No anomalies found")
    ).toBeVisible({ timeout: 5_000 });

    console.log("✅ CLEAN: All assertions passed");
  });

  test("ANOMALY-RICH: anomaly_rich_ledger + anomaly_rich_settlement → 11 flagged", async ({
    page,
  }) => {
    await uploadFiles(
      page,
      path.join(FIXTURES, "valid/anomaly_rich_ledger.csv"),
      path.join(FIXTURES, "valid/anomaly_rich_settlement.csv")
    );

    await page.click('button:has-text("Run Reconciliation")');

    // Should navigate to Run Summary page
    await page.waitForURL("**/runs/**", { timeout: 15_000 });

    // Wait for Run Summary to load
    await expect(page.locator("h1:has-text('Run Summary')")).toBeVisible({
      timeout: 10_000,
    });

    // Verify stats: Total Records = 14, Flagged = 11
    await expect(page.locator("text=Total Records")).toBeVisible();
    await expect(page.locator("text=14")).toBeVisible();
    await expect(page.locator("text=11")).toBeVisible();

    // Navigate to Flags page
    await page.click('a:has-text("View Flags")');
    await page.waitForURL("**/runs/**/flags", { timeout: 10_000 });

    // Verify flag types are present (FlagBadge renders human-readable labels)
    await expect(page.locator("text=Amount Mismatch").first()).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.locator("text=Duplicate").first()).toBeVisible();
    await expect(page.locator("text=Missing Settlement").first()).toBeVisible();
    await expect(page.locator("text=Timing Anomaly").first()).toBeVisible();

    // Count flag rows
    const flagRows = page.locator('a[href^="/flags/"]');
    await expect(flagRows).toHaveCount(11, { timeout: 5_000 });

    console.log("✅ ANOMALY-RICH: All assertions passed");
  });
});

// ============================================================
// INVALID DATASETS — each should show a validation error
// ============================================================

test.describe("Invalid Datasets", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  const invalidCases: Array<{
    name: string;
    file: string;
    expectedError: string;
  }> = [
    {
      name: "missing_column",
      file: "invalid/missing_column.csv",
      expectedError: "Missing required columns: currency",
    },
    {
      name: "negative_amount",
      file: "invalid/negative_amount.csv",
      expectedError: "amount must be a positive number",
    },
    {
      name: "duplicate_transaction_id",
      file: "invalid/duplicate_transaction_id.csv",
      expectedError: "Duplicate transaction_id values found",
    },
    {
      name: "mixed_currency",
      file: "invalid/mixed_currency.csv",
      expectedError: "Multiple currencies found",
    },
    {
      name: "empty_file",
      file: "invalid/empty_file.csv",
      expectedError: "File contains no data rows",
    },
    {
      name: "bad_timestamp",
      file: "invalid/bad_timestamp.csv",
      expectedError: "timestamp could not be parsed",
    },
  ];

  for (const { name, file, expectedError } of invalidCases) {
    test(`REJECT: ${name} → shows "${expectedError}"`, async ({ page }) => {
      await uploadFiles(
        page,
        path.join(FIXTURES, file),
        path.join(FIXTURES, "valid/clean_settlement.csv")
      );

      await page.click('button:has-text("Run Reconciliation")');

      // Should stay on the upload page — no navigation away
      // And show an error message in [role="alert"]
      const errorEl = page.locator('[role="alert"]');
      await expect(errorEl).toBeVisible({ timeout: 10_000 });

      const errorText = await errorEl.textContent();
      console.log(`${name} → error: "${errorText}"`);
      expect(errorText).toContain(expectedError);

      console.log(`✅ REJECT (${name}): Assertion passed`);
    });
  }
});
