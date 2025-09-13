const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  // Basic Information
  firstName: {
    type: String,
    required: [true, 'First name is required'],
    trim: true,
    maxlength: [50, 'First name cannot exceed 50 characters']
  },
  lastName: {
    type: String,
    required: [true, 'Last name is required'],
    trim: true,
    maxlength: [50, 'Last name cannot exceed 50 characters']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
  },
  password: {
    type: String,
    required: [true, 'Password is required'],
    minlength: [6, 'Password must be at least 6 characters'],
    select: false // Don't include password in queries by default
  },
  phone: {
    type: String,
    trim: true,
    match: [/^[0-9]{10}$/, 'Please enter a valid 10-digit phone number']
  },

  // Premium Features
  isPremium: {
    type: Boolean,
    default: false
  },
  premiumPlan: {
    type: String,
    enum: ['none', 'student', 'premium'],
    default: 'none'
  },
  premiumExpiry: {
    type: Date,
    default: null
  },
  premiumFeatures: {
    aiAnswers: {
      type: Number,
      default: 0,
      max: [1000, 'AI answers limit exceeded']
    },
    questionBookmarks: [{
      questionPaperId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'QuestionPaper'
      },
      addedAt: {
        type: Date,
        default: Date.now
      }
    }],
    repeatedQuestions: {
      type: Boolean,
      default: false
    },
    studyMaterials: {
      type: Boolean,
      default: false
    }
  },

  // Account Status
  isActive: {
    type: Boolean,
    default: true
  },
  isEmailVerified: {
    type: Boolean,
    default: false
  },
  emailVerificationToken: String,
  emailVerificationExpiry: Date,

  // Password Reset
  passwordResetToken: String,
  passwordResetExpiry: Date,

  // Profile
  profilePicture: {
    type: String,
    default: null
  },
  dateOfBirth: Date,
  gender: {
    type: String,
    enum: ['male', 'female', 'other', 'prefer-not-to-say'],
    default: 'prefer-not-to-say'
  },
  location: {
    city: String,
    state: String,
    country: {
      type: String,
      default: 'India'
    }
  },

  // Academic Information
  academicInfo: {
    currentCourse: String,
    currentSemester: Number,
    university: {
      type: String,
      default: 'Mumbai University'
    },
    graduationYear: Number
  },

  // Usage Statistics
  usageStats: {
    lastLogin: {
      type: Date,
      default: Date.now
    },
    totalLogins: {
      type: Number,
      default: 1
    },
    questionPapersViewed: {
      type: Number,
      default: 0
    },
    questionPapersDownloaded: {
      type: Number,
      default: 0
    }
  },

  // Payment History
  paymentHistory: [{
    orderId: String,
    amount: Number,
    currency: {
      type: String,
      default: 'INR'
    },
    plan: String,
    status: {
      type: String,
      enum: ['pending', 'completed', 'failed', 'refunded'],
      default: 'pending'
    },
    paymentMethod: String,
    paidAt: Date,
    razorpayPaymentId: String,
    razorpayOrderId: String
  }],

  // Preferences
  preferences: {
    notifications: {
      email: {
        type: Boolean,
        default: true
      },
      sms: {
        type: Boolean,
        default: false
      },
      push: {
        type: Boolean,
        default: true
      }
    },
    theme: {
      type: String,
      enum: ['light', 'dark', 'auto'],
      default: 'auto'
    },
    language: {
      type: String,
      default: 'en'
    }
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual for full name
userSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Virtual for premium status
userSchema.virtual('isPremiumActive').get(function() {
  if (!this.isPremium) return false;
  if (!this.premiumExpiry) return false;
  return this.premiumExpiry > new Date();
});

// Virtual for days until premium expires
userSchema.virtual('daysUntilExpiry').get(function() {
  if (!this.isPremiumActive) return 0;
  const diffTime = this.premiumExpiry - new Date();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
});

// Indexes for better query performance
userSchema.index({ email: 1 });
userSchema.index({ isPremium: 1 });
userSchema.index({ premiumExpiry: 1 });
userSchema.index({ 'premiumFeatures.questionBookmarks.questionPaperId': 1 });

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(parseInt(process.env.BCRYPT_ROUNDS) || 12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to compare password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

// Method to check premium status
userSchema.methods.checkPremiumStatus = function() {
  if (!this.isPremium) return false;
  if (!this.premiumExpiry) return false;
  
  const now = new Date();
  if (this.premiumExpiry < now) {
    this.isPremium = false;
    this.premiumPlan = 'none';
    this.premiumExpiry = null;
    return false;
  }
  
  return true;
};

// Method to add question bookmark
userSchema.methods.addBookmark = function(questionPaperId) {
  if (!this.isPremiumActive) {
    throw new Error('Premium subscription required for bookmarks');
  }
  
  const existingBookmark = this.premiumFeatures.questionBookmarks.find(
    bookmark => bookmark.questionPaperId.toString() === questionPaperId.toString()
  );
  
  if (!existingBookmark) {
    this.premiumFeatures.questionBookmarks.push({ questionPaperId });
  }
  
  return this;
};

// Method to remove question bookmark
userSchema.methods.removeBookmark = function(questionPaperId) {
  this.premiumFeatures.questionBookmarks = this.premiumFeatures.questionBookmarks.filter(
    bookmark => bookmark.questionPaperId.toString() !== questionPaperId.toString()
  );
  
  return this;
};

// Method to use AI answer
userSchema.methods.useAIAnswer = function() {
  if (!this.isPremiumActive) {
    throw new Error('Premium subscription required for AI answers');
  }
  
  if (this.premiumFeatures.aiAnswers <= 0) {
    throw new Error('AI answer limit reached for this month');
  }
  
  this.premiumFeatures.aiAnswers -= 1;
  return this;
};

// Static method to find premium users
userSchema.statics.findPremiumUsers = function() {
  return this.find({
    isPremium: true,
    premiumExpiry: { $gt: new Date() }
  });
};

// Static method to find expired premium users
userSchema.statics.findExpiredPremiumUsers = function() {
  return this.find({
    isPremium: true,
    premiumExpiry: { $lt: new Date() }
  });
};

module.exports = mongoose.model('User', userSchema);
