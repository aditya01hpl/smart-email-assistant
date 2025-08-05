import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-toastify';
import { getEmailDetails, sendReply, regenerateReply } from '../services/api';
import { formatTimestamp, getSenderInitials, getAvatarColor } from '../services/api';

const EmailModal = ({ email, onClose, onUpdate }) => {
  const [emailDetails, setEmailDetails] = useState(email);
  const [replyContent, setReplyContent] = useState('');
  const [sending, setSending] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('summary'); // summary, fullEmail, reply
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEmailDetails();
    if (email.draft_reply && !email.has_reply) {
      setReplyContent(email.draft_reply);
    }
  }, [email.id]);

  const loadEmailDetails = async () => {
    try {
      setLoading(true);
      const response = await getEmailDetails(email.id);
      setEmailDetails(response.email);
    } catch (error) {
      console.error('Error loading email details:', error);
      toast.error('Failed to load email details');
    } finally {
      setLoading(false);
    }
  };

  const handleSendReply = async () => {
    if (!replyContent.trim()) {
      toast.error('Please write a reply before sending');
      return;
    }

    try {
      setSending(true);
      await sendReply(email.id, { content: replyContent });
      toast.success('Reply sent successfully!');
      
      // Update email status
      const updatedEmail = { ...emailDetails, has_reply: true };
      setEmailDetails(updatedEmail);
      onUpdate(updatedEmail);
      
      // Close modal after successful send
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (error) {
      console.error('Error sending reply:', error);
      toast.error('Failed to send reply: ' + (error.response?.data?.error || error.message));
    } finally {
      setSending(false);
    }
  };

  const handleRegenerateReply = async () => {
    try {
      setRegenerating(true);
      const response = await regenerateReply(email.id);
      setReplyContent(response.draft_reply);
      toast.success('New reply generated!');
    } catch (error) {
      console.error('Error regenerating reply:', error);
      toast.error('Failed to generate new reply');
    } finally {
      setRegenerating(false);
    }
  };

  const modalVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 }
  };

  const initials = getSenderInitials(emailDetails.sender_name, emailDetails.sender);
  const avatarColor = getAvatarColor(emailDetails.sender);
  const timeAgo = formatTimestamp(emailDetails.timestamp);

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          variants={modalVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 ${avatarColor} rounded-full flex items-center justify-center`}>
                  <span className="text-white font-semibold">{initials}</span>
                </div>
                <div>
                  <h2 className="text-xl font-bold">{emailDetails.sender_name || emailDetails.sender}</h2>
                  <p className="text-blue-100">{emailDetails.sender}</p>
                  <p className="text-blue-200 text-sm">{timeAgo}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {!emailDetails.has_reply && (
                  <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Needs Reply
                  </span>
                )}
                <button
                  onClick={onClose}
                  className="text-white hover:text-gray-200 transition-colors p-2 rounded-lg hover:bg-white hover:bg-opacity-20"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Subject */}
            <div className="mt-4">
              <h3 className="text-lg font-semibold">{emailDetails.subject}</h3>
            </div>

            {/* Tabs */}
            <div className="flex space-x-1 mt-4">
              {['summary', 'fullEmail', 'reply'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === tab
                      ? 'bg-white text-blue-600'
                      : 'text-blue-100 hover:text-white hover:bg-white hover:bg-opacity-20'
                  }`}
                >
                  {tab === 'summary' && 'Summary'}
                  {tab === 'fullEmail' && 'Full Email'}
                  {tab === 'reply' && 'Reply'}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              </div>
            ) : (
              <>
                {/* Summary Tab */}
    {activeTab === 'summary' && (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            AI Summary
          </h4>
          {emailDetails.summary ? (
            <div className="text-blue-800 space-y-1">
              {emailDetails.summary.split('\n').map((line, idx) => (
                line.trim() && (
                  <p key={idx} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{line.replace('•', '').trim()}</span>
                  </p>
                )
              ))}
            </div>
          ) : (
            <p className="text-blue-700">No summary available</p>
          )}
        </div>
      </motion.div>
    )}

    {/* Full Email Tab */}
    {activeTab === 'fullEmail' && (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="prose max-w-none"
      >
        <div 
          className="email-html-content" 
          dangerouslySetInnerHTML={{ __html: emailDetails.full_body || emailDetails.body }} 
        />
      </motion.div>
    )}


                {/* Reply Tab */}
                {activeTab === 'reply' && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    {emailDetails.has_reply ? (
                      <div className="bg-green-50 rounded-lg p-4 border border-green-200 text-center">
                        <svg className="w-12 h-12 text-green-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 className="text-lg font-semibold text-green-900">Already Replied</h3>
                        <p className="text-green-700">You have already sent a reply to this email.</p>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-gray-900">Compose Reply</h4>
                          <button
                            onClick={handleRegenerateReply}
                            disabled={regenerating}
                            className="flex items-center space-x-2 px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                          >
                            {regenerating ? (
                              <>
                                <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                                <span>Regenerating...</span>
                              </>
                            ) : (
                              <>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                <span>Regenerate</span>
                              </>
                            )}
                          </button>
                        </div>

                        <textarea
                          value={replyContent}
                          onChange={(e) => setReplyContent(e.target.value)}
                          placeholder="Write your reply here..."
                          rows={12}
                          className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        />

                        <div className="flex items-center justify-between">
                          <div className="text-sm text-gray-500">
                            {replyContent.length} characters
                          </div>
                          
                          <div className="flex space-x-3">
                            <button
                              onClick={onClose}
                              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={handleSendReply}
                              disabled={sending || !replyContent.trim()}
                              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
                            >
                              {sending ? (
                                <>
                                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                                  <span>Sending...</span>
                                </>
                              ) : (
                                <>
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                  </svg>
                                  <span>Send Reply</span>
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      </>
                    )}
                  </motion.div>
                )}
              </>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default EmailModal;