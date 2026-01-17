---
name: tailored-resume-generator
description: >-
  Analyzes job descriptions and 生成s tailored resumes that highlight relevant
  experience, skills, and achievements to maximize interview chances
trigger: when_needed
language: zh-TW
adapted_from: openskills/tailored-resume-generator
version: 1.0.0-antigravity
original_license: Unknown
---
# TAILORED-RESUME-GENERATOR 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/tailored-resume-generator  
> **語言**: 繁體中文

## 概述

Analyzes job descriptions and 生成s tailored resumes that highlight relevant experience, skills, and achievements to maximize interview chances

---


# Tailored Resume Generator

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## When to Use This Skill

- Applying for a specific job position
- Customizing your resume for different industries or roles
- Highlighting relevant experience for career transitions
- Optimizing your resume for ATS (Applicant Tracking Systems)
- Creating multiple resume versions for different job applications
- Emphasizing specific skills mentioned in job postings

## What This Skill Does

1. **Analyzes Job Descriptions**: Extracts key requirements, skills, qualifications, and keywords from job postings
2. **Identifies Priorities**: Determines what employers value most based on the job description language and structure
3. **Tailors Content**: Reorganizes and emphasizes relevant experience, skills, and achievements
4. **Optimizes Keywords**: Incorporates ATS-friendly keywords naturally throughout the resume
5. **Formats Professionally**: Creates clean, professional resume layouts suitable for various formats
6. **Provides Recommendations**: Suggests improvements and highlights gaps to address

## How to Use

### Basic 使用方式
Provide a job description and your background information:


詳細內容請參閱：[example_6.txt](examples/example_6.txt)


### With Existing Resume
Upload or paste your current resume along with the job description:


詳細內容請參閱：[example_7.txt](examples/example_7.txt)


### Career Transition
When changing industries or roles:


詳細內容請參閱：[example_8.txt](examples/example_8.txt)


## Example

**User Request:**

詳細內容請參閱：[example_9.txt](examples/example_9.txt)


**Generated Output:**


詳細內容請參閱：[example_10.txt](examples/example_10.txt)


**Additional Recommendations:**
- Consider adding any specific healthcare projects or certifications
- Quantify more achievements with metrics when possible
- If you have experience with R or advanced statistical methods, add them
- Consider mentioning any familiarity with healthcare regulations (HIPAA, etc.)

---

## Instructions

When a user requests resume tailoring:

### 1. Gather Information

**Job Description Analysis**:
- Request the full job description if not provided
- Ask for the company name and job title

**Candidate Background**:
- If user provides existing resume, use it as the foundation
- If not, request:
  - Work history (job titles, companies, dates, responsibilities)
  - Education background
  - Key skills and technical proficiencies
  - Notable achievements and metrics
  - Certifications or awards
  - Any other relevant information

### 2. Analyze Job 需求

Extract and prioritize:
- **Must-have qualifications**: Years of experience, required skills, education
- **Key skills**: Technical tools, methodologies, competencies
- **Soft skills**: Communication, leadership, teamwork
- **Industry knowledge**: Domain-specific experience
- **Keywords**: Repeated terms, phrases, and buzzwords for ATS optimization
- **Company values**: Cultural fit indicators from job description

Create a mental map of:
- Priority 1: Critical requirements (deal-breakers)
- Priority 2: Important qualifications (strongly desired)
- Priority 3: Nice-to-have skills (bonus points)

### 3. Map Candidate Experience to 需求

For each job requirement:
- Identify matching experience from candidate's background
- Find transferable skills if no direct match
- Note gaps that need to be addressed or de-emphasized
- Identify unique strengths to highlight

### 4. Structure the Tailored Resume

**Professional Summary** (3-4 lines):
- Lead with years of experience in the target role/field
- Include top 3-4 required skills from job description
- Mention industry experience if relevant
- Highlight unique value proposition

**Technical/Core Skills Section**:
- Group skills by category matching job requirements
- List required tools and technologies first
- Use exact terminology from job description
- Only include skills you can substantiate with experience

**Professional Experience**:
- For each role, emphasize responsibilities and achievements aligned with job requirements
- Use action verbs: Led, Developed, Implemented, Optimized, Managed, Created, Analyzed
- **Quantify achievements**: Include numbers, percentages, timeframes, scale
- Reorder bullet points to prioritize most relevant experience
- Use keywords naturally from job description
- Format: **[Action Verb] + [What] + [How/Why] + [Result/Impact]**

**Education**:
- List degrees, certifications relevant to position
- Include relevant coursework if early career
- Add certifications that match job requirements

**Optional Sections** (if applicable):
- Certifications & 授權s
- Publications or Speaking Engagements
- Awards & Recognition
- Volunteer Work (if relevant to role)
- Projects (especially for technical roles)

### 5. Optimize for ATS (Applicant Tracking Systems)

- Use standard section headings (Professional Experience, Education, Skills)
- Incorporate exact keywords from job description naturally
- Avoid tables, graphics, headers/footers, or complex formatting
- Use standard fonts and bullet points
- Include both acronyms and full terms (e.g., "SQL (Structured Query Language)")
- Match job title terminology where truthful

### 6. Format and Present

**Format Options**:
- **Markdown**: Clean, readable, easy to copy
- **Plain Text**: ATS-optimized, safe for all systems
- **Tips for Word/PDF**: Provide formatting guidance

**Resume Structure Guidelines**:
- Keep to 1 page for <10 years experience, 2 pages for 10+ years
- Use consistent formatting and spacing
- Ensure contact information is prominent
- Use reverse chronological order (most recent first)
- Maintain clean, scannable layout with white space

### 7. Provide Strategic Recommendations

After presenting the tailored resume, offer:

**Strengths Analysis**:
- What makes this candidate competitive
- Unique qualifications to emphasize in cover letter or interview

**Gap Analysis**:
- 需求 not fully met
- Suggestions for addressing gaps (courses, projects, reframing experience)

**Interview Preparation Tips**:
- Key talking points aligned with resume
- Stories to prepare based on job requirements
- Questions to ask that demonstrate fit

**Cover Letter Hooks**:
- Suggest 2-3 opening lines for cover letter
- Key achievements to expand upon

### 8. Iterate and Refine

Ask if user wants to:
- Adjust emphasis or tone
- Add or remove sections
- Generate alternative versions for different roles
- Create format variations (traditional vs. modern)
- Develop role-specific versions (if applying to multiple similar positions)

### 9. 最佳實踐 to Follow

**Do**:
- Be truthful and accurate - never fabricate experience
- Use industry-standard terminology
- Quantify achievements with specific metrics
- Tailor each resume to specific job
- Proofread for grammar and consistency
- Keep language concise and impactful

**Don't**:
- Include personal information (age, marital status, photo unless requested)
- Use first-person pronouns (I, me, my)
- Include references ("available upon request" is outdated)
- List every job if career is 20+ years (focus on relevant, recent experience)
- Use generic templates without customization
- Exceed 2 pages unless very senior role

### 10. Special Considerations

**Career Changers**:
- Use functional or hybrid resume format
- Emphasize transferable skills
- Create compelling narrative in summary
- Focus on relevant projects and coursework

**Recent Graduates**:
- Lead with education
- Include relevant coursework, projects, internships
- Emphasize leadership in student organizations
- Include GPA if 3.5+

**Senior Executives**:
- Lead with executive summary
- Focus on leadership and strategic impact
- Include board memberships, speaking engagements
- Emphasize revenue growth, team building, vision

**Technical Roles**:
- Include technical skills section prominently
- List programming languages, frameworks, tools
- Include GitHub, portfolio, or project links
- Mention methodologies (Agile, Scrum, etc.)

**Creative Roles**:
- Include link to portfolio
- Highlight creative achievements and campaigns
- Mention tools and software proficiencies
- Consider more creative formatting (while maintaining ATS compatibility)

---

## Tips for Best Results

- **Be specific**: Provide complete job descriptions and detailed background information
- **Share metrics**: Include numbers, percentages, and quantifiable achievements when describing your experience
- **Indicate format preference**: Let the skill know if you need ATS-optimized, creative, or traditional format
- **Mention constraints**: Share any specific requirements (page limits, sections to include/exclude)
- **Iterate**: Don't hesitate to ask for revisions or alternative approaches
- **Multiple applications**: Generate separate tailored versions for different roles

## Privacy Note

This skill processes your personal and professional information to generate tailored resumes. Always review the output before submitting to ensure accuracy and appropriateness. Remove or modify any information you prefer not to share with potential employers.


---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 與 `skills/_base/architecture.md` 架構模式一致
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

可搭配以下技能使用：
- `systematic-debugging` - 系統化除錯
- `verification-before-completion` - 完成前驗證