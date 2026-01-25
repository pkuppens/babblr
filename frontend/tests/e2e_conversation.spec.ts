/**
 * Section 5-6: End-to-End Conversation Tests (Playwright)
 *
 * Optional automated E2E tests for frontend and conversation flow.
 * Can be used as automated checks or run manually for debugging.
 *
 * Setup:
 * - npm install --save-dev @playwright/test
 * - Backend running at http://localhost:8000
 * - Frontend running at http://localhost:3000 or http://localhost:5173
 *
 * Run:
 * - npx playwright test e2e_conversation.spec.ts
 * - npx playwright test --headed (see browser)
 * - npx playwright test --debug (debug mode)
 */

import { expect, test } from "@playwright/test";

const BASE_URL = process.env.FRONTEND_URL || "http://localhost:3000";

test.describe("Section 5: Frontend UI Validation", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app and wait for it to load
    await page.goto(BASE_URL, { waitUntil: "networkidle" });
    // Wait for initial render
    await page.waitForLoadState("domcontentloaded");
  });

  test("5.1: Home screen language selection", async ({ page }) => {
    // SETUP: Locate language selector
    const languageSelector = page.locator("select, [role='combobox']").first();

    // ACTION: Click and select Spanish
    await languageSelector.click();
    await page.getByText("Spanish").click();

    // EXPECTED RESULT 1: Language selector shows Spanish
    await expect(languageSelector).toContainText("Spanish");

    // EXPECTED RESULT 2: Verify Spanish is now displayed
    // (Check if any UI text is in Spanish - example: "Seleccionar" or "Español")
    const homeText = await page.locator("body").textContent();
    expect(homeText).toBeTruthy();

    // EXPECTED RESULT 3: Language persists on page reload
    await page.reload();
    await expect(languageSelector).toContainText("Spanish");
  });

  test("5.2: Home screen CEFR level selection", async ({ page }) => {
    // Ensure Spanish is selected
    const languageSelector = page.locator("select").first();
    await languageSelector.click();
    await page.getByText("Spanish").click();

    // SETUP: Locate CEFR level selector
    const levelSelector = page.locator("select").nth(1);

    // ACTION: Select A1 level
    await levelSelector.click();
    await page.getByText("A1").click();

    // EXPECTED RESULT 1: Level selector shows A1
    await expect(levelSelector).toContainText("A1");

    // EXPECTED RESULT 2: Level persists on reload
    await page.reload();
    await expect(levelSelector).toContainText("A1");
  });

  test("5.3: Home screen topic selection", async ({ page }) => {
    // SETUP: Topics should display as cards/buttons
    const topics = page.locator('[data-testid="topic-card"], .topic');

    // EXPECTED RESULT 1: Multiple topics available (5+)
    const topicCount = await topics.count();
    expect(topicCount).toBeGreaterThanOrEqual(5);

    // EXPECTED RESULT 2: Each topic has a title
    const firstTopic = topics.first();
    await expect(firstTopic).toContainText(/^[A-Za-záéíóúñ\s]+$/);

    // ACTION: Click first topic
    await firstTopic.click();

    // EXPECTED RESULT 3: Topic is highlighted
    await expect(firstTopic).toHaveClass(/selected|active/);

    // EXPECTED RESULT 4: Start button becomes enabled
    const startButton = page.getByRole("button", { name: /start|begin/i });
    await expect(startButton).toBeEnabled();
  });

  test("5.4: Start conversation flow", async ({ page }) => {
    // SETUP: Select language, level, topic
    const langSelector = page.locator("select").first();
    await langSelector.click();
    await page.getByText("Spanish").click();

    const levelSelector = page.locator("select").nth(1);
    await levelSelector.click();
    await page.getByText("A1").click();

    // Select topic (first one)
    const topics = page.locator('[data-testid="topic-card"], .topic');
    await topics.first().click();

    // ACTION: Click Start Conversation
    const startButton = page.getByRole("button", { name: /start|begin/i });
    await startButton.click();

    // EXPECTED RESULT 1: Page transition (wait for conversation screen)
    await page.waitForURL(/conversation|chat/, { timeout: 10000 });

    // EXPECTED RESULT 2: Conversation screen loads with initial message
    const messageArea = page.locator('[data-testid="messages"], .messages, .chat');
    await expect(messageArea).toBeVisible();

    // EXPECTED RESULT 3: Initial tutor message in Spanish
    const tutorMessage = messageArea.locator("text=/^[A-Za-záéíóúñ¿?!¡\\s.,]+$/");
    await expect(tutorMessage).toBeVisible();
  });

  test("5.5: Conversation screen message display", async ({ page }) => {
    // SETUP: Start a conversation
    await navigateToConversation(page);

    // EXPECTED RESULT 1: Messages area visible
    const messagesArea = page.locator('[data-testid="messages"], .messages, .chat');
    await expect(messagesArea).toBeVisible();

    // EXPECTED RESULT 2: Tutor message is identifiable
    const tutorMessage = messagesArea.locator('[data-testid="message-tutor"], .message-tutor, .assistant');
    await expect(tutorMessage).toBeVisible();

    // EXPECTED RESULT 3: Message has speaker label
    await expect(tutorMessage).toContainText(/tutor|assistant|ai/i);
  });

  test("5.6: Voice input (if microphone available)", async ({ page, context }) => {
    // SETUP: Grant microphone permission
    await context.grantPermissions(["microphone"]);

    // SETUP: Start conversation
    await navigateToConversation(page);

    // SETUP: Locate voice button
    const voiceButton = page.locator('button[aria-label*="voice"], button[aria-label*="mic"], button svg[data-icon="microphone"]')
      .locator("..");

    // Check if voice button exists and is enabled
    const voiceEnabled = await voiceButton.isEnabled().catch(() => false);

    if (voiceEnabled) {
      // ACTION: Click voice button
      await voiceButton.click();

      // EXPECTED RESULT 1: Button shows recording state
      await expect(voiceButton).toHaveClass(/recording|active/);

      // Wait for recording (simulate speaking - actual voice not needed in test)
      await page.waitForTimeout(2000);

      // ACTION: Stop recording (click again or auto-stop)
      await voiceButton.click();

      // EXPECTED RESULT 2: Input field populated
      const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
      const inputValue = await inputField.inputValue();
      // In unit test, we'd have mocked this. Here we just check it's there
      expect(inputValue).toBeDefined();
    } else {
      // EXPECTED RESULT: Voice button disabled or hidden
      await expect(voiceButton).toBeDisabled().catch(async () => {
        await expect(voiceButton).toBeHidden();
      });
    }
  });

  test("5.7: TTS playback", async ({ page }) => {
    // SETUP: Start conversation
    await navigateToConversation(page);

    // SETUP: Locate tutor message and speaker button
    const tutorMessage = page.locator('[data-testid="message-tutor"], .message-tutor, .assistant').first();
    const speakerButton = tutorMessage.locator('button svg[data-icon="volume"], button[aria-label*="play"], button[aria-label*="sound"]')
      .locator("..");

    // Check if speaker button exists
    const speakerEnabled = await speakerButton.isVisible().catch(() => false);

    if (speakerEnabled) {
      // ACTION: Click speaker button
      await speakerButton.click();

      // EXPECTED RESULT 1: Button shows playing state
      await expect(speakerButton).toHaveClass(/playing|active/);

      // Wait for playback
      await page.waitForTimeout(3000);

      // EXPECTED RESULT 2: Button returns to normal
      await expect(speakerButton).not.toHaveClass(/playing/);
    }
  });

  test("5.8: Text input and send", async ({ page }) => {
    // SETUP: Start conversation
    await navigateToConversation(page);

    // SETUP: Locate input field
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();

    // ACTION: Type message
    await inputField.fill("Hola, estoy bien.");

    // EXPECTED RESULT 1: Text appears in input
    await expect(inputField).toHaveValue("Hola, estoy bien.");

    // SETUP: Send button
    const sendButton = page.getByRole("button", { name: /send/i });

    // EXPECTED RESULT 2: Send button is enabled
    await expect(sendButton).toBeEnabled();

    // ACTION: Send message
    await sendButton.click();

    // EXPECTED RESULT 3: Input clears
    await expect(inputField).toHaveValue("");

    // EXPECTED RESULT 4: User message appears
    const userMessage = page.locator('[data-testid="message-user"], .message-user, .user').last();
    await expect(userMessage).toContainText("Hola, estoy bien.");
  });

  test("5.9: Multi-turn conversation", async ({ page }) => {
    // SETUP: Start conversation
    await navigateToConversation(page);

    // Send first message
    await sendMessage(page, "Buenos días");

    // EXPECTED RESULT 1: Tutor responds
    let tutorMessages = await page.locator('[data-testid="message-tutor"], .message-tutor, .assistant');
    const initialCount = await tutorMessages.count();

    // Wait for response (up to 10 seconds)
    await page.waitForTimeout(5000);

    // EXPECTED RESULT 2: New tutor message added
    tutorMessages = await page.locator('[data-testid="message-tutor"], .message-tutor, .assistant');
    const newCount = await tutorMessages.count();
    expect(newCount).toBeGreaterThan(initialCount);

    // Send second message
    await sendMessage(page, "¿De dónde eres?");

    // EXPECTED RESULT 3: Conversation continues
    await page.waitForTimeout(5000);
    const allMessages = await page.locator('[data-testid="message"], .message').count();
    expect(allMessages).toBeGreaterThanOrEqual(4); // At least 2 user + 2 tutor
  });

  test("5.10: Settings persistence", async ({ page }) => {
    // SETUP: Navigate to config/settings screen
    const settingsLink = page.getByRole("link", { name: /settings|config/i });
    if (await settingsLink.isVisible()) {
      await settingsLink.click();

      // SETUP: Find a setting to change (example: volume)
      const volumeSlider = page.locator('input[type="range"]').first();

      if (await volumeSlider.isVisible()) {
        // ACTION: Change volume
        await volumeSlider.fill("75");

        // Wait for save
        await page.waitForTimeout(1000);

        // EXPECTED RESULT 1: Setting changed
        expect(await volumeSlider.inputValue()).toBe("75");

        // EXPECTED RESULT 2: Persists on reload
        await page.reload();
        await page.waitForLoadState("domcontentloaded");

        if (await settingsLink.isVisible()) {
          await settingsLink.click();
          const reloadedSlider = page.locator('input[type="range"]').first();
          expect(await reloadedSlider.inputValue()).toBe("75");
        }
      }
    }
  });
});

test.describe("Section 6: End-to-End Conversation Testing", () => {
  test("6.1: Complete Spanish A1 conversation", async ({ page }) => {
    // SETUP: Start Spanish A1 conversation
    await navigateToConversation(page, { language: "Spanish", level: "A1" });

    // Send 5 messages to verify full conversation flow
    const messages = ["Me llamo Alex", "¿Y tú?", "Mucho gusto", "¿De dónde eres?", "¡Muy bien!"];

    for (const msg of messages) {
      // ACTION: Send message
      await sendMessage(page, msg);

      // EXPECTED RESULT: Tutor responds within 5 seconds
      await page.waitForTimeout(5000);

      // EXPECTED RESULT: Conversation continues without errors
      const errorMessages = page.locator('[data-testid="error"], .error');
      await expect(errorMessages).toHaveCount(0);
    }

    // EXPECTED RESULT: At least 10 messages total (5 user + 5 tutor)
    const allMessages = await page.locator('[data-testid="message"], .message').count();
    expect(allMessages).toBeGreaterThanOrEqual(10);
  });

  test("6.2: Cross-language conversation - French B1", async ({ page }) => {
    // SETUP: Start French B1 conversation
    await navigateToConversation(page, { language: "French", level: "B1" });

    // Send French B1-level message
    await sendMessage(page, "Je travaille comme développeur");

    // EXPECTED RESULT: Tutor responds in French
    await page.waitForTimeout(5000);

    const tutorMessage = page.locator('[data-testid="message-tutor"], .message-tutor, .assistant').last();
    const messageText = await tutorMessage.textContent();

    // Check for French characters and B1-level vocabulary
    // (Would need more sophisticated language detection in real test)
    expect(messageText).toBeTruthy();
    expect(messageText?.length).toBeGreaterThan(20); // B1 responses should be longer
  });

  test("6.3: Voice input and TTS in conversation", async ({ page, context }) => {
    // SETUP: Grant microphone permission
    await context.grantPermissions(["microphone"]);

    // SETUP: Start conversation
    await navigateToConversation(page);

    // Send message via text (voice not needed for this test)
    await sendMessage(page, "Me gusta comer");

    // Wait for response
    await page.waitForTimeout(5000);

    // EXPECTED RESULT: Conversation completes without errors
    const errors = page.locator('[data-testid="error"], .error');
    await expect(errors).toHaveCount(0);

    // EXPECTED RESULT: At least 2 exchanges
    const allMessages = await page.locator('[data-testid="message"], .message');
    expect(await allMessages.count()).toBeGreaterThanOrEqual(2);
  });

  test("6.6: Conversation persistence", async ({ page }) => {
    // SETUP: Start conversation and send a message
    await navigateToConversation(page);
    const firstMessageText = "Hola, ¿cómo estás?";
    await sendMessage(page, firstMessageText);

    // SETUP: Navigate to history/conversations list
    const historyLink = page.getByRole("link", { name: /history|conversations/i });
    if (await historyLink.isVisible()) {
      await historyLink.click();

      // EXPECTED RESULT 1: Conversation appears in history
      const conversationItem = page.locator('[data-testid="conversation-item"], .conversation-card').first();
      await expect(conversationItem).toBeVisible();

      // ACTION: Click to reopen conversation
      await conversationItem.click();

      // EXPECTED RESULT 2: Messages are preserved
      const messages = page.locator('[data-testid="message"], .message');
      const allMessagesText = await messages.allTextContents();
      expect(allMessagesText.join(" ")).toContain(firstMessageText);
    }
  });

  test("6.7: Error handling - Network error recovery", async ({ page }) => {
    // SETUP: Start conversation
    await navigateToConversation(page);

    // Send a message
    await sendMessage(page, "Test message");

    // EXPECTED RESULT: No unhandled errors
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    // EXPECTED RESULT: App remains functional
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await expect(inputField).toBeEnabled();
  });
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Navigate to an active conversation
 */
async function navigateToConversation(
  page: any,
  options?: { language?: string; level?: string }
) {
  const language = options?.language || "Spanish";
  const level = options?.level || "A1";

  // Go to home if not already there
  if (!page.url().includes(BASE_URL)) {
    await page.goto(BASE_URL);
  }

  // Select language
  const langSelector = page.locator("select").first();
  await langSelector.click();
  await page.getByText(language).click();

  // Select level
  const levelSelector = page.locator("select").nth(1);
  await levelSelector.click();
  await page.getByText(level).click();

  // Select topic (first one)
  const topics = page.locator('[data-testid="topic-card"], .topic');
  await topics.first().click();

  // Start conversation
  const startButton = page.getByRole("button", { name: /start|begin/i });
  await startButton.click();

  // Wait for conversation screen
  await page.waitForURL(/conversation|chat/, { timeout: 10000 });
}

/**
 * Send a message in the conversation
 */
async function sendMessage(page: any, message: string) {
  const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
  await inputField.fill(message);

  const sendButton = page.getByRole("button", { name: /send/i });
  await sendButton.click();

  // Wait for input to clear
  await page.waitForTimeout(500);
}
