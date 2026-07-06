# Category Management Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to create new expense categories dynamically through the UI, with backend persistence and immediate availability in the expense form dropdown.

**Architecture:** Add a `create` action to the existing Rails `Api::CategoriesController`, add model validations for `Category`, and build a frontend `AddCategoryModal` component. Update `ExpenseForm` to fetch categories from the API (instead of hardcoded constants) and render an "Add Category" button that opens the modal. After creation, the dropdown refreshes with the new category auto-selected.

**Design decision — emojis for new categories:** No emoji picker. New categories default to the `📦` fallback (same as the existing "Other" category). This is already handled by `getCategoryEmoji()` in `frontend/src/constants/categoryEmojis.ts:18`, which returns `"📦"` for any name not in the hardcoded map. No code changes needed.

**Tech Stack:** Ruby on Rails 7.2 (API-only), React 18 + TypeScript + Vite, MySQL 8.0

---

### Task 1: Category Model Validations

**Files:**
- Modify: `backend/app/models/category.rb`
- Modify: `backend/spec/factories/categories.rb`
- Modify: `backend/spec/models/category_spec.rb`

- [ ] **Step 1: Write model spec for validations**

Write to `backend/spec/models/category_spec.rb`:

```ruby
require 'rails_helper'

RSpec.describe Category, type: :model do
  describe 'validations' do
    it 'is valid with a name' do
      category = Category.new(name: 'Food')
      expect(category).to be_valid
    end

    it 'is invalid without a name' do
      category = Category.new(name: nil)
      expect(category).not_to be_valid
      expect(category.errors[:name]).to include("can't be blank")
    end

    it 'is invalid with a duplicate name' do
      Category.create!(name: 'Food')
      category = Category.new(name: 'Food')
      expect(category).not_to be_valid
      expect(category.errors[:name]).to include("has already been taken")
    end
  end

  describe 'associations' do
    it 'has many expenses' do
      expect(Category.new).to respond_to(:expenses)
    end
  end
end
```

- [ ] **Step 2: Update factory to generate unique names** (needed once validations enforce uniqueness)

Write to `backend/spec/factories/categories.rb`:

```ruby
FactoryBot.define do
  factory :category do
    sequence(:name) { |n| "Category #{n}" }
  end
end
```

- [ ] **Step 3: Run model specs to verify they fail**

Run: `docker compose run --rm backend bundle exec rspec spec/models/category_spec.rb`

Expected: 3 failures (no name validation, no uniqueness validation)

- [ ] **Step 4: Add validations to Category model**

Write to `backend/app/models/category.rb`:

```ruby
class Category < ApplicationRecord
  has_many :expenses, dependent: :destroy

  validates :name, presence: true, uniqueness: { case_sensitive: false }
end
```

- [ ] **Step 5: Run model specs to verify they pass**

Run: `docker compose run --rm backend bundle exec rspec spec/models/category_spec.rb`

Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/category.rb backend/spec/models/category_spec.rb backend/spec/factories/categories.rb
git commit -m "feat: add presence and uniqueness validations to Category model"
```

---

### Task 2: Backend Category Create Endpoint

**Files:**
- Modify: `backend/app/controllers/api/categories_controller.rb`
- Modify: `backend/config/routes.rb`
- Modify: `backend/spec/requests/api/categories_spec.rb`

- [ ] **Step 1: Write request specs for POST /api/categories**

Write to `backend/spec/requests/api/categories_spec.rb` (append after existing describe block):

```ruby
  describe "POST /api/categories" do
    context "with valid params" do
      it "creates a new category and returns it" do
        expect {
          post "/api/categories", params: { category: { name: "Investments" } }
        }.to change(Category, :count).by(1)

        expect(response).to have_http_status(:created)
        json = JSON.parse(response.body)
        expect(json["name"]).to eq("Investments")
      end
    end

    context "with missing name" do
      it "returns unprocessable entity with errors" do
        post "/api/categories", params: { category: { name: "" } }

        expect(response).to have_http_status(:unprocessable_entity)
        json = JSON.parse(response.body)
        expect(json["errors"]).to include("Name can't be blank")
      end
    end

    context "with duplicate name" do
      before { Category.create!(name: "Food") }

      it "returns unprocessable entity with errors" do
        post "/api/categories", params: { category: { name: "Food" } }

        expect(response).to have_http_status(:unprocessable_entity)
        json = JSON.parse(response.body)
        expect(json["errors"]).to include("Name has already been taken")
      end
    end
  end
```

- [ ] **Step 2: Run request specs to verify they fail**

Run: `docker compose run --rm backend bundle exec rspec spec/requests/api/categories_spec.rb`

Expected: New tests FAIL (no route, no create action)

- [ ] **Step 3: Add :create to categories route**

Write to `backend/config/routes.rb`:

```ruby
Rails.application.routes.draw do
  get "up" => "rails/health#show", as: :rails_health_check

  namespace :api do
    resources :categories, only: [ :index, :create ]
    resources :expenses, only: [ :index, :create, :update, :destroy ]
  end
end
```

- [ ] **Step 4: Add create action to categories controller**

Write to `backend/app/controllers/api/categories_controller.rb`:

```ruby
class Api::CategoriesController < ApplicationController
  def index
    categories = Category.order(:name)
    render json: categories
  end

  def create
    category = Category.new(category_params)

    if category.save
      render json: category, status: :created
    else
      render json: { errors: category.errors.full_messages }, status: :unprocessable_entity
    end
  end

  private

  def category_params
    params.require(:category).permit(:name)
  end
end
```

- [ ] **Step 5: Run request specs to verify they pass**

Run: `docker compose run --rm backend bundle exec rspec spec/requests/api/categories_spec.rb`

Expected: All PASS (existing index tests + new create tests)

- [ ] **Step 6: Run full spec suite to check for regressions**

Run: `docker compose run --rm backend bundle exec rspec`

Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add backend/config/routes.rb backend/app/controllers/api/categories_controller.rb backend/spec/requests/api/categories_spec.rb
git commit -m "feat: add POST /api/categories endpoint to create new categories"
```

---

### Task 3: Frontend API Service — createCategory

**Files:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: Add createCategory function**

Append after `fetchCategories` in `frontend/src/services/api.ts`:

```typescript
/**
 * Create a new category
 */
export async function createCategory(
  name: string,
): Promise<{ id: number; name: string }> {
  const response = await fetch(`${API_BASE_URL}/categories`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ category: { name } }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.errors?.[0] || "Failed to create category");
  }

  return response.json();
}
```

- [ ] **Step 2: Verify frontend builds**

Run: `cd frontend && npx tsc --noEmit`

Expected: No errors (no callers yet, just export)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add createCategory API function to frontend service"
```

---

### Task 4: AddCategoryModal Component

**Files:**
- Create: `frontend/src/components/AddCategoryModal.tsx`

- [ ] **Step 1: Create the AddCategoryModal component**

Write to `frontend/src/components/AddCategoryModal.tsx`:

```typescript
import React, { useState } from "react";
import { createCategory } from "../services/api";
import { Modal, TextField, Button } from "../vibes";

interface AddCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCategoryCreated: (name: string) => void;
}

export function AddCategoryModal({
  isOpen,
  onClose,
  onCategoryCreated,
}: AddCategoryModalProps) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();

    if (!trimmed) {
      setError("Category name is required");
      return;
    }

    try {
      setIsSubmitting(true);
      setError("");
      await createCategory(trimmed);
      onCategoryCreated(trimmed);
      setName("");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create category");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setName("");
    setError("");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Add New Category">
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
      >
        <TextField
          label="Category Name"
          type="text"
          placeholder="Enter category name"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setError("");
          }}
          error={error}
          fullWidth
          required
          autoFocus
        />

        <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
          <Button
            type="submit"
            variant="primary"
            disabled={isSubmitting}
            fullWidth
          >
            {isSubmitting ? "Creating..." : "Create Category"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        </div>
      </form>
    </Modal>
  );
}
```

- [ ] **Step 2: Verify frontend compiles**

Run: `cd frontend && npx tsc --noEmit`

Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AddCategoryModal.tsx
git commit -m "feat: add AddCategoryModal component for creating categories"
```

---

### Task 5: Update ExpenseForm to Use Dynamic Categories

**Files:**
- Modify: `frontend/src/components/ExpenseForm.tsx`

- [ ] **Step 1: Rewrite ExpenseForm to fetch categories and integrate AddCategoryModal**

Write to `frontend/src/components/ExpenseForm.tsx`:

```typescript
import React, { useState, useEffect } from "react";
import { ExpenseFormData } from "../types";
import { fetchCategories } from "../services/api";
import { TextField, SelectBox, Button } from "../vibes";
import { useExpenseForm } from "../hooks/useExpenseForm";
import { AddCategoryModal } from "./AddCategoryModal";

interface ExpenseFormProps {
  initialData?: Partial<ExpenseFormData>;
  onSubmit: (data: ExpenseFormData) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
}

export function ExpenseForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = "Add Expense",
}: ExpenseFormProps) {
  const [categories, setCategories] = useState<string[]>([]);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);

  const { formData, errors, isSubmitting, handleChange, handleSubmit } =
    useExpenseForm({
      initialData,
      onSubmit,
    });

  useEffect(() => {
    fetchCategories()
      .then((data) => setCategories(data.map((c) => c.name)))
      .catch(() => setCategories([]));
  }, []);

  const refreshCategories = async () => {
    try {
      const data = await fetchCategories();
      setCategories(data.map((c) => c.name));
    } catch {
      // keep current categories on error
    }
  };

  const handleCategoryCreated = (name: string) => {
    handleChange("category", name);
    refreshCategories();
  };

  const formStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  };

  const categoryRowStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "flex-end",
    gap: "0.5rem",
  };

  const buttonGroupStyle: React.CSSProperties = {
    display: "flex",
    gap: "0.5rem",
    marginTop: "0.5rem",
  };

  const categoryOptions = categories.map((category) => ({
    value: category,
    label: category,
  }));

  return (
    <>
      <form onSubmit={handleSubmit} style={formStyle}>
        <TextField
          label="Amount"
          type="number"
          step="0.01"
          placeholder="0.00"
          value={formData.amount}
          onChange={(e) => handleChange("amount", e.target.value)}
          error={errors.amount}
          fullWidth
          required
        />

        <TextField
          label="Description"
          type="text"
          placeholder="Enter description"
          value={formData.description}
          onChange={(e) => handleChange("description", e.target.value)}
          error={errors.description}
          fullWidth
          required
        />

        <div style={categoryRowStyle}>
          <div style={{ flex: 1 }}>
            <SelectBox
              label="Category"
              options={categoryOptions}
              value={formData.category}
              onChange={(e) => handleChange("category", e.target.value)}
              error={errors.category}
              fullWidth
              required
            />
          </div>
          <Button
            type="button"
            variant="secondary"
            onClick={() => setIsCategoryModalOpen(true)}
          >
            + Add
          </Button>
        </div>

        <TextField
          label="Date"
          type="date"
          value={formData.date}
          onChange={(e) => handleChange("date", e.target.value)}
          error={errors.date}
          fullWidth
          required
        />

        <div style={buttonGroupStyle}>
          <Button
            type="submit"
            variant="primary"
            disabled={isSubmitting}
            fullWidth
          >
            {isSubmitting ? "Submitting..." : submitLabel}
          </Button>
          {onCancel && (
            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}
        </div>
      </form>

      <AddCategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onCategoryCreated={handleCategoryCreated}
      />
    </>
  );
}
```

- [ ] **Step 2: Verify frontend typechecks**

Run: `cd frontend && npx tsc --noEmit`

Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ExpenseForm.tsx
git commit -m "feat: replace hardcoded categories with API-fetched dynamic categories in ExpenseForm"
```

---

### Task 6: End-to-End Verification

- [ ] **Step 1: Run full backend test suite**

Run: `docker compose run --rm backend bundle exec rspec`

Expected: All PASS

- [ ] **Step 2: Verify frontend typechecks and builds**

Run: `cd frontend && npx tsc --noEmit`

Expected: No errors

- [ ] **Step 3: Commit (if any cleanup needed)**

Only needed if Step 1 or 2 required fixes.

---

## Self-Review

**1. Spec coverage:**
- [x] "Add Category button in prominent location" → Task 5: "+ Add" button next to category select in ExpenseForm
- [x] "Modal dialog to input new category details" → Task 4: AddCategoryModal component
- [x] "Backend endpoint to persist new category" → Task 2: POST /api/categories
- [x] "Updated category list after creation" → Task 5: `handleCategoryCreated` refreshes categories and auto-selects new one

**2. Placeholder scan:** No TBDs, TODOs, or vague instructions. All code is concrete.

**3. Type consistency:**
- `createCategory(name: string)` in api.ts returns `{ id: number; name: string }` — matches backend response
- `AddCategoryModalProps.onCategoryCreated(name: string)` — name type matches createCategory param
- ExpenseForm uses `handleChange("category", name)` directly from the hook — no extra hook changes needed

**4. Emoji handling:** `getCategoryEmoji()` in `categoryEmojis.ts:18` already returns `"📦"` for any name not in the hardcoded map. New categories get the fallback automatically with zero code changes.
