# Deploying to Vercel

This guide will help you deploy your Fit With COACH Daniel application to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Git](https://git-scm.com/downloads) installed on your computer
3. [Vercel CLI](https://vercel.com/docs/cli) (optional, but recommended)

## Step 1: Prepare Your Project

Make sure your project has the following files:
- `vercel.json` - Configuration for Vercel
- `requirements.txt` - Python dependencies
- `wsgi.py` - Entry point for Vercel
- `.gitignore` - To exclude unnecessary files

## Step 2: Set Up a Database

Since Vercel doesn't provide persistent storage, you'll need to use an external database service:

1. Sign up for a free PostgreSQL database at [Supabase](https://supabase.com/) or [Railway](https://railway.app/)
2. Get your database connection string
3. You'll add this as an environment variable in Vercel

## Step 3: Deploy to Vercel

### Option 1: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy your project:
   ```bash
   vercel
   ```

4. Follow the prompts to complete the deployment

### Option 2: Using Vercel Dashboard

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket)
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your repository
5. Configure your project settings
6. Click "Deploy"

## Step 4: Configure Environment Variables

After deployment, you need to set up your environment variables:

1. Go to your project in the Vercel Dashboard
2. Click on "Settings" > "Environment Variables"
3. Add the following variables:
   - `SECRET_KEY` - A secure random string
   - `DATABASE_URL` - Your PostgreSQL connection string
   - `BREVO_API_KEY` - Your Brevo API key for email functionality

## Step 5: Initialize the Database

After deployment, you need to initialize your database:

1. Go to your project in the Vercel Dashboard
2. Click on "Deployments"
3. Find your latest deployment and click on the three dots (...)
4. Select "Redeploy"
5. In the "Build and Output Settings" section, add the following command:
   ```
   python -c "from app import init_db; init_db()"
   ```
6. Click "Redeploy"

## Troubleshooting

If you encounter issues:

1. Check the Vercel deployment logs for errors
2. Make sure all environment variables are set correctly
3. Verify that your database connection string is correct
4. Check that your application is compatible with serverless functions

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Flask on Vercel](https://vercel.com/docs/frameworks/flask)
- [PostgreSQL on Vercel](https://vercel.com/docs/storage/vercel-postgres) 