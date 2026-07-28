import re

with open("c:/Users/Admin/Downloads/GrowthGPT Project/growthgpt/templates/simulate.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the form HTML entirely
new_form = """<form class="sim-form glass wizard-form" action="{{ url_for('simulate_run') }}" method="POST" id="simForm" novalidate style="max-width: 820px; margin: 0 auto 60px; padding: 36px 40px;" enctype="multipart/form-data">

  <!-- Top Pipeline Tracker inside form card -->
  <div class="wizard-progress" id="wizardProgress" style="margin-bottom: 32px; background: rgba(250, 243, 232, 0.75); padding: 14px 20px;">
    <div class="wizard-step-indicator" data-step="1" title="Campaign & Product Name">
      <span class="wizard-dot">1</span>
      <span class="wizard-step-label">Names</span>
    </div>
    <div class="wizard-track"><div class="wizard-track-fill"></div></div>

    <div class="wizard-step-indicator" data-step="2" title="Objective">
      <span class="wizard-dot">2</span>
      <span class="wizard-step-label">Goal</span>
    </div>
    <div class="wizard-track"><div class="wizard-track-fill"></div></div>

    <div class="wizard-step-indicator" data-step="3" title="Product Details">
      <span class="wizard-dot">3</span>
      <span class="wizard-step-label">Product</span>
    </div>
    <div class="wizard-track"><div class="wizard-track-fill"></div></div>

    <div class="wizard-step-indicator" data-step="4" title="Target Audience">
      <span class="wizard-dot">4</span>
      <span class="wizard-step-label">Audience</span>
    </div>
    <div class="wizard-track"><div class="wizard-track-fill"></div></div>

    <div class="wizard-step-indicator" data-step="5" title="Campaign Message">
      <span class="wizard-dot">5</span>
      <span class="wizard-step-label">Message</span>
    </div>
    <div class="wizard-track"><div class="wizard-track-fill"></div></div>

    <div class="wizard-step-indicator" data-step="6" title="Budget Context">
      <span class="wizard-dot">6</span>
      <span class="wizard-step-label">Budget</span>
    </div>
    <div class="wizard-track"><div class="wizard-track-fill"></div></div>

    <div class="wizard-step-indicator" data-step="7" title="Review & Submit">
      <span class="wizard-dot">7</span>
      <span class="wizard-step-label">Review</span>
    </div>
  </div>

  <!-- Step 1 — Campaign Name + Product Name -->
  <div class="wizard-panel active" data-panel="1">
    <h2 class="wizard-panel-title">📦 Step 1: Campaign &amp; Product Name</h2>
    <p class="wizard-panel-sub">Give your campaign and product memorable titles.</p>
    <div class="form-grid">
      <div class="field field-full">
        <label for="campaign_name">Campaign Name <span class="req">*</span></label>
        <div class="field-input-wrap">
          <span class="field-input-icon">🏷️</span>
          <input type="text" id="campaign_name" name="campaign_name" placeholder="e.g. Summer Sale 2026" required maxlength="120">
        </div>
        <span class="field-error" data-error-for="campaign_name">Please enter a campaign name to continue.</span>
      </div>
      <div class="field field-full">
        <label for="product_name">Product Name <span class="req">*</span></label>
        <div class="field-input-wrap">
          <span class="field-input-icon">🛍️</span>
          <input type="text" id="product_name" name="product_name" placeholder="e.g. NovaBrew Cold Coffee" required maxlength="120">
        </div>
        <span class="field-error" data-error-for="product_name">Please enter a product name to continue.</span>
      </div>
    </div>
  </div>

  <!-- Step 2 — Campaign Objective -->
  <div class="wizard-panel" data-panel="2">
    <h2 class="wizard-panel-title">🎯 Step 2: Campaign Objective</h2>
    <p class="wizard-panel-sub">Select the primary goal for this marketing initiative.</p>
    <div class="form-grid">
      <div class="field field-full">
        <label for="objective">Campaign Goal</label>
        <div class="field-input-wrap">
          <span class="field-input-icon">🎯</span>
          <select id="objective" name="objective" style="width: 100%; padding-left: 42px;">
            <option value="Awareness">🔔 Awareness — Reach maximum new audience</option>
            <option value="Engagement" selected>💬 Engagement — Maximize comments, shares & likes</option>
            <option value="Conversion">🛒 Conversion — Drive sales & signups</option>
            <option value="Retention">🔁 Retention — Drive loyalty & repeat customers</option>
          </select>
        </div>
      </div>
    </div>
  </div>

  <!-- Step 3 — Category + Product Description + Price + Advertisement Image -->
  <div class="wizard-panel" data-panel="3">
    <h2 class="wizard-panel-title">📝 Step 3: Product Details</h2>
    <p class="wizard-panel-sub">Describe what you are offering and the key benefits it provides.</p>
    <div class="form-grid">
      <div class="field field-full">
        <label for="category">Category</label>
        <div class="field-input-wrap">
          <span class="field-input-icon">📂</span>
          <input type="text" id="category" name="category" placeholder="e.g. Beverages, Software, Fashion">
        </div>
      </div>
      <div class="field field-full">
        <label for="product_description">Product Description</label>
        <textarea id="product_description" name="product_description" rows="3"
          placeholder="What are you selling? What problem does it solve for your customers?"></textarea>
      </div>
      <div class="field field-full">
        <label for="price">Price</label>
        <div class="field-input-wrap">
          <span class="field-input-icon">💵</span>
          <input type="text" id="price" name="price" placeholder="e.g. $19.99">
        </div>
      </div>
      <div class="field field-full">
        <label for="advertisement_image">Advertisement Image</label>
        <div class="field-input-wrap">
          <span class="field-input-icon" style="top: 10px; transform: none;">🖼️</span>
          <input type="file" id="advertisement_image" name="advertisement_image" accept="image/*" style="padding: 8px 10px 8px 42px;">
        </div>
      </div>
    </div>
  </div>

  <!-- Step 4 — Target Audience + Age + Gender + Income + Occupation + Location + Interests -->
  <div class="wizard-panel" data-panel="4">
    <h2 class="wizard-panel-title">👥 Step 4: Target Audience</h2>
    <p class="wizard-panel-sub">Specify who this campaign is intended to reach.</p>
    <div class="form-grid">
      <div class="field field-full">
        <label for="target_audience">Target Audience Overview</label>
        <textarea id="target_audience" name="target_audience" rows="2"
          placeholder="e.g. College students in Tier-2 Indian cities, budget-conscious"></textarea>
      </div>
      <div class="field field-full" style="display: flex; gap: 15px;">
        <div style="flex: 1;">
          <label for="age">Age</label>
          <input type="text" id="age" name="age" placeholder="e.g. 18-24">
        </div>
        <div style="flex: 1;">
          <label for="gender">Gender</label>
          <select id="gender" name="gender" style="width: 100%;">
            <option value="Any" selected>Any</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>
      <div class="field field-full" style="display: flex; gap: 15px;">
        <div style="flex: 1;">
          <label for="income">Income</label>
          <input type="text" id="income" name="income" placeholder="e.g. $50k+">
        </div>
        <div style="flex: 1;">
          <label for="occupation">Occupation</label>
          <input type="text" id="occupation" name="occupation" placeholder="e.g. Student">
        </div>
      </div>
      <div class="field field-full">
        <label for="location">Location</label>
        <div class="field-input-wrap">
          <span class="field-input-icon">📍</span>
          <input type="text" id="location" name="location" placeholder="e.g. New York, NY">
        </div>
      </div>
      <div class="field field-full">
        <label for="interests">Interests</label>
        <textarea id="interests" name="interests" rows="2" placeholder="e.g. Tech, Fashion, Travel"></textarea>
      </div>
    </div>
  </div>

  <!-- Step 5 — Marketing Platform + Headline + Campaign Description + CTA + Offer + Competitor Names -->
  <div class="wizard-panel" data-panel="5">
    <h2 class="wizard-panel-title">✍️ Step 5: Campaign Message</h2>
    <p class="wizard-panel-sub">Provide the specifics of your marketing collateral.</p>
    <div class="form-grid">
      <div class="field field-full">
        <label for="marketing_platform">Marketing Platform</label>
        <div class="field-input-wrap">
          <span class="field-input-icon">📱</span>
          <input type="text" id="marketing_platform" name="marketing_platform" placeholder="e.g. Instagram, LinkedIn">
        </div>
      </div>
      <div class="field field-full">
        <label for="headline">Headline</label>
        <div class="field-input-wrap">
          <span class="field-input-icon">📰</span>
          <input type="text" id="headline" name="headline" placeholder="e.g. Refresh Your Summer">
        </div>
      </div>
      <div class="field field-full">
        <label for="campaign_description">Campaign Description / Ad Copy <span class="req">*</span></label>
        <textarea id="campaign_description" name="campaign_description" rows="3"
          placeholder="Paste the main ad copy or promotional message..." required></textarea>
        <span class="field-error" data-error-for="campaign_description">Please enter your campaign description or ad copy.</span>
      </div>
      <div class="field field-full" style="display: flex; gap: 15px;">
        <div style="flex: 1;">
          <label for="cta">Call to Action (CTA)</label>
          <input type="text" id="cta" name="cta" placeholder="e.g. Shop Now">
        </div>
        <div style="flex: 1;">
          <label for="offer">Offer</label>
          <input type="text" id="offer" name="offer" placeholder="e.g. 20% Off">
        </div>
      </div>
      <div class="field field-full">
        <label for="competitor_names">Competitor Names <span class="optional">(optional)</span></label>
        <textarea id="competitor_names" name="competitor_names" rows="2" placeholder="e.g. Brand X, Brand Y"></textarea>
      </div>
    </div>
  </div>

  <!-- Step 6 — Budget Context -->
  <div class="wizard-panel" data-panel="6">
    <h2 class="wizard-panel-title">💳 Step 6: Budget & Duration</h2>
    <p class="wizard-panel-sub">Add optional budget and timeframe details.</p>
    <div class="form-grid">
      <div class="field field-full">
        <label for="budget">Budget Context <span class="optional">(optional)</span></label>
        <div class="field-input-wrap">
          <span class="field-input-icon">💳</span>
          <input type="text" id="budget" name="budget" placeholder="e.g. $50,000 / month">
        </div>
      </div>
      <div class="field field-full">
        <label for="campaign_duration">Campaign Duration <span class="optional">(optional)</span></label>
        <div class="field-input-wrap">
          <span class="field-input-icon">⏳</span>
          <input type="text" id="campaign_duration" name="campaign_duration" placeholder="e.g. 3 Months">
        </div>
      </div>
    </div>
  </div>

  <!-- Step 7 — Review & Confirm -->
  <div class="wizard-panel" data-panel="7">
    <h2 class="wizard-panel-title">📋 Step 7: Review &amp; Run Simulation</h2>
    <p class="wizard-panel-sub">Review your campaign details before initiating the AI Digital Twin simulation.</p>

    <div class="review-card">
      <div class="review-row">
        <div class="review-row-head">
          <span class="review-row-label">1. Campaign & Product Name</span>
          <button type="button" class="review-edit" data-goto="1">Edit Step 1</button>
        </div>
        <div class="review-row-body">
          <div class="review-field"><span class="review-field-key">Campaign Name</span><span class="review-field-val" data-review="campaign_name">—</span></div>
          <div class="review-field"><span class="review-field-key">Product Name</span><span class="review-field-val" data-review="product_name">—</span></div>
        </div>
      </div>

      <div class="review-row">
        <div class="review-row-head">
          <span class="review-row-label">2. Campaign Goal</span>
          <button type="button" class="review-edit" data-goto="2">Edit Step 2</button>
        </div>
        <div class="review-row-body">
          <div class="review-field"><span class="review-field-key">Objective</span><span class="review-field-val" data-review="objective">—</span></div>
        </div>
      </div>

      <div class="review-row">
        <div class="review-row-head">
          <span class="review-row-label">3. Product Details</span>
          <button type="button" class="review-edit" data-goto="3">Edit Step 3</button>
        </div>
        <div class="review-row-body">
          <div class="review-field"><span class="review-field-key">Category</span><span class="review-field-val" data-review="category">—</span></div>
          <div class="review-field review-field-block"><span class="review-field-key">Description</span><span class="review-field-val" data-review="product_description">—</span></div>
          <div class="review-field"><span class="review-field-key">Price</span><span class="review-field-val" data-review="price">—</span></div>
        </div>
      </div>

      <div class="review-row">
        <div class="review-row-head">
          <span class="review-row-label">4. Target Audience</span>
          <button type="button" class="review-edit" data-goto="4">Edit Step 4</button>
        </div>
        <div class="review-row-body">
          <div class="review-field review-field-block"><span class="review-field-key">Audience</span><span class="review-field-val" data-review="target_audience">—</span></div>
          <div class="review-field"><span class="review-field-key">Demographics</span><span class="review-field-val" data-review="demo_summary">—</span></div>
        </div>
      </div>

      <div class="review-row">
        <div class="review-row-head">
          <span class="review-row-label">5. Campaign Message</span>
          <button type="button" class="review-edit" data-goto="5">Edit Step 5</button>
        </div>
        <div class="review-row-body">
          <div class="review-field review-field-block"><span class="review-field-key">Ad Copy</span><span class="review-field-val" data-review="campaign_description">—</span></div>
          <div class="review-field"><span class="review-field-key">Platform</span><span class="review-field-val" data-review="marketing_platform">—</span></div>
        </div>
      </div>

      <div class="review-row">
        <div class="review-row-head">
          <span class="review-row-label">6. Budget & Duration</span>
          <button type="button" class="review-edit" data-goto="6">Edit Step 6</button>
        </div>
        <div class="review-row-body">
          <div class="review-field"><span class="review-field-key">Budget</span><span class="review-field-val" data-review="budget">—</span></div>
          <div class="review-field"><span class="review-field-key">Duration</span><span class="review-field-val" data-review="campaign_duration">—</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Wizard Navigation Bar -->
  <div class="wizard-nav">
    <button type="button" class="btn btn-ghost btn-large wizard-prev" id="wizardPrev">← Previous</button>
    <button type="button" class="btn btn-primary btn-large wizard-next" id="wizardNext">Next Step →</button>
    <button type="submit" class="btn btn-primary btn-large btn-submit wizard-submit hidden" id="submitBtn">
      <span class="btn-label">Start AI Analysis</span>
      <span class="btn-emoji">💰</span>
    </button>
  </div>
</form>"""

pattern_form = re.compile(r'<form class="sim-form glass wizard-form"(.*?)</form>', re.DOTALL)
content = pattern_form.sub(new_form, content)

# Now update the javascript
js_required = """    const requiredByStep = {
      1: ['campaign_name', 'product_name'],
      5: ['campaign_description'],
    };"""

pattern_required = re.compile(r'const requiredByStep = \{.*?\};', re.DOTALL)
content = pattern_required.sub(js_required, content)

js_populate = """    function populateReview() {
      const defaults = {
        campaign_name: 'Untitled campaign',
        product_name: 'Untitled product',
        objective: 'Engagement',
        category: 'Not specified',
        product_description: 'Not specified',
        price: 'Not specified',
        target_audience: 'Not specified',
        campaign_description: 'Not specified',
        marketing_platform: 'Not specified',
        budget: 'Not specified',
        campaign_duration: 'Not specified'
      };
      
      const combinedDemo = [
        document.getElementById('age')?.value,
        document.getElementById('gender')?.value !== 'Any' ? document.getElementById('gender')?.value : '',
        document.getElementById('income')?.value,
        document.getElementById('occupation')?.value,
        document.getElementById('location')?.value
      ].filter(x => x && x.trim() !== '').join(', ') || 'Not specified';
      
      const target = document.querySelector(`[data-review="demo_summary"]`);
      if (target) target.textContent = combinedDemo;

      Object.keys(defaults).forEach(id => {
        const input = document.getElementById(id);
        const target = document.querySelector(`[data-review="${id}"]`);
        if (!input || !target) return;
        let val = input.value.trim();
        if (id === 'objective') {
          val = input.options[input.selectedIndex] ? input.options[input.selectedIndex].text : val;
        }
        target.textContent = val || defaults[id];
      });
    }"""

pattern_populate = re.compile(r'function populateReview\(\) \{.*?\}', re.DOTALL)
content = pattern_populate.sub(js_populate, content)

with open("c:/Users/Admin/Downloads/GrowthGPT Project/growthgpt/templates/simulate.html", "w", encoding="utf-8") as f:
    f.write(content)

print("simulate.html updated successfully!")
