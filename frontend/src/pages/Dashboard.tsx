import { Upload, FileText, Search, Wand2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const quickActions = [
  {
    name: 'Import Documents',
    description: 'Upload your resume, performance reviews, and other documents',
    href: '/import',
    icon: Upload,
    color: 'bg-blue-500',
  },
  {
    name: 'View Master Resume',
    description: 'Review and edit your comprehensive master resume',
    href: '/master-resume',
    icon: FileText,
    color: 'bg-green-500',
  },
  {
    name: 'Research',
    description: 'Market trends and company research',
    href: '/research',
    icon: Search,
    color: 'bg-purple-500',
  },
  {
    name: 'Generate Application',
    description: 'Create tailored resume and cover letter',
    href: '/generate',
    icon: Wand2,
    color: 'bg-orange-500',
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Welcome to GroundedCV</h1>
        <p className="mt-1 text-gray-600">Your story. Truthfully tailored.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {quickActions.map((action) => (
          <Link
            key={action.name}
            to={action.href}
            className="card flex items-start gap-4 transition-shadow hover:shadow-md"
          >
            <div className={`${action.color} rounded-lg p-3`}>
              <action.icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{action.name}</h3>
              <p className="mt-1 text-sm text-gray-600">{action.description}</p>
            </div>
          </Link>
        ))}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900">Getting Started</h2>
        <div className="mt-4 space-y-4">
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-medium text-primary-600">
              1
            </div>
            <div>
              <p className="font-medium text-gray-900">Import your documents</p>
              <p className="text-sm text-gray-600">
                Upload your base resume, performance reviews, and any other relevant documents.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-medium text-primary-600">
              2
            </div>
            <div>
              <p className="font-medium text-gray-900">Generate your Master Resume</p>
              <p className="text-sm text-gray-600">
                Our AI will synthesize all your documents into a comprehensive master resume.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-medium text-primary-600">
              3
            </div>
            <div>
              <p className="font-medium text-gray-900">Tailor your applications</p>
              <p className="text-sm text-gray-600">
                Paste a job description and get AI-tailored resumes and cover letters.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="card bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
        <div className="mt-4 flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-green-500"></div>
          <span className="text-sm text-gray-600">Backend connected</span>
        </div>
      </div>
    </div>
  );
}
